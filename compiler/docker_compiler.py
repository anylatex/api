# coding: utf-8

import os
import time
import base64
import shutil
import docker
from string import Template

from models.users import User
from models.pdfs import PDF
from models.images import Image
from models.tasks import Task


class TaskMonitor:

    """Monitor of processing uncompiled tasks in db."""

    def __init__(self, docker_socket_path,
                 texlive_docker_image,
                 compiler_docker_volume,
                 structure_dir='', templates={},
                 compile_cmd=None, compile_tmp_dir='/compiler-tmp',
                 compiler_number=None, db_scan_interval=1, **other):
        self.name = self.__class__.__name__
        self.docker_client = docker.from_env()
        self.texlive_docker_image = texlive_docker_image
        self.compiler_docker_volume = compiler_docker_volume
        # compiler settings
        if not structure_dir:
            structure_dir = os.path.dirname(os.path.realpath(__file__))
            structure_dir = os.path.join(structure_dir, 'structures')
        self.structure_dir = structure_dir
        self.template_configs = templates
        if not compiler_number:
            compiler_number = os.cpu_count()
        self.compiler_number = compiler_number
        if not compile_cmd:
            raise ValueError("no compile command provided.")
        self.compile_cmd = compile_cmd
        self.compile_tmp_dir = compile_tmp_dir
        if not os.path.exists(self.compile_tmp_dir):
            os.mkdir(self.compile_tmp_dir)
        # other settings
        self.db_scan_interval = db_scan_interval
        self.compiling_containers = {}
        self.compilers = []

    def scan(self):
        results = Task.find_all()
        compile_tasks = []
        for result in results:
            task = Task(**result)
            if task.status == 'new':
                compile_tasks.append(task)
            elif task.status == "compiling":
                pass
            elif task.status == "finished":
                pass
            elif task.status == "failed":
                # TODO
                pass
            else:
                print("unknown task's status:", task.status)
        return compile_tasks

    def start(self):
        for _ in range(self.compiler_number):
            compiler_name = 'texlive-' + str(_)
            try:
                # use existed containers
                # TODO: catch exit signal and kill these containers
                container = self.docker_client.containers.get(compiler_name)
            except docker.errors.NotFound:
                container = self.docker_client.containers.run(
                    self.texlive_docker_image,
                    command='/bin/bash',
                    stdin_open=True,
                    tty=True,
                    detach=True,
                    name='texlive-' + str(_),
                    volumes={
                        self.compiler_docker_volume: {
                            'bind': self.compile_tmp_dir,
                            'mode': 'rw'
                        }
                    }
                )
            finally:
                self.compilers.append(container)

        while True:
            # scan tasks in db and assign new tasks
            new_tasks = self.scan()
            idle_compilers = [
                container for container in self.compilers
                if container not in self.compiling_containers
            ]
            for i, new_task in enumerate(new_tasks[:len(idle_compilers)]):
                # assign a new task
                self.assign_new_task(idle_compilers[i], new_task)
            # print('assign %d new tasks, %d tasks remain'
            #       % (assigned_num, len(new_tasks) - assigned_num))

            # check if any tasks finished
            finished_containers = []
            for container, task in self.compiling_containers.items():
                if os.path.exists(task.finish_file):
                    self.process_result(task)
                    finished_containers.append(container)
            for finished_container in finished_containers:
                self.compiling_containers.pop(finished_container)

            time.sleep(self.db_scan_interval)

    def assign_new_task(self, container, task):
        task.status = 'compiling'
        task.update_to_db()
        print('Start', 'processing task:', task.task_id)
        # create temp directory
        compile_tmp_dir = os.path.join(
            self.compile_tmp_dir, task.user_id + task.document_id)
        if not os.path.exists(compile_tmp_dir):
            os.mkdir(compile_tmp_dir)
        filename = task.document_id + '.tex'
        filepath = os.path.join(compile_tmp_dir, filename)
        pdfname = task.document_id + '.pdf'
        pdfpath = os.path.join(compile_tmp_dir, pdfname)
        task.pdfpath = pdfpath
        # get template's arguments and write them into the structure document
        args = task.args
        part_args = task.part_args
        sub_dict = dict(documentclass=task.template, body=task.body)
        # get structure document path
        structure = self.template_configs[task.template]['structure']
        # TODO: need to optimize
        if args['references']:
            biber_structure = structure.replace(
                '.structure',
                '-biber.structure'
            )
            structure_path = os.path.join(self.structure_dir, biber_structure)
            if os.path.exists(structure_path):
                structure = biber_structure
                args.pop('references')
        structure_path = os.path.join(self.structure_dir, structure)
        with open(structure_path, 'r') as f:
            structure_t = Template(f.read())
        if args:
            for arg, value in args.items():
                sub_dict[arg] = value
        if part_args:
            for arg, value in part_args.items():
                sub_dict[arg] = value
        latex = structure_t.substitute(sub_dict)
        # fetch images in DB and save them to the compiling directory
        for image_name in task.images:
            image_id, image_type = image_name.split('.')
            image = Image(image_id=image_id, user_id=task.user_id)
            try:
                image.load_from_db()
            except Exception as e:
                print(e)
                continue
            image_content = base64.b64decode(image.content.encode())
            image_path = os.path.join(compile_tmp_dir, image_name)
            with open(image_path, 'wb') as f:
                f.write(image_content)
        # move cls to compile dir if exists
        cls_path = self.template_configs[task.template].get('cls_path')
        if cls_path:
            shutil.copy(
                cls_path,
                os.path.join(compile_tmp_dir, os.path.split(cls_path)[-1])
            )
        # write tex file
        with open(filepath, 'w') as f:
            f.write(latex)
        # start compiling
        command = self.compile_cmd.format(
            filepath = filepath,
            outdir = compile_tmp_dir
        )
        # create a file when finishing compiling the .tex file
        finish_file = os.path.join(compile_tmp_dir, 'finished')
        command += '; touch %s' % finish_file
        command = '/bin/bash -c "%s"' % command
        task.finish_file = finish_file
        container.exec_run(
            command,
            detach=True
        )
        print('Container', container.name, 'assigned a new task:', command)
        self.compiling_containers[container] = task

    def process_result(self, task):
        try:
            os.remove(task.finish_file)
            delattr(task, 'finish_file')
            pdfpath = task.pdfpath
            delattr(task, 'pdfpath')
            if not os.path.exists(pdfpath):
                raise Exception('No pdf generated')
            # get pdf b64 string and put into db
            with open(pdfpath, 'rb') as f:
                pdf_content = f.read()
            pdf_b64 = base64.b64encode(pdf_content).decode('utf-8')
            compiled_time = str(int(time.time()))
            pdf = PDF(data=pdf_b64, compiled_time=compiled_time)
            pdf.create_in_db()
            task.pdf_id = pdf.pdf_id
            user = User(user_id=task.user_id)
            user.load_from_db()
            user.compiled_pdfs.append(pdf.pdf_id)
            user.update_to_db()
            # update task into task
            task.status = "finished"
            task.update_to_db()
            print('Ends', 'processing result:', task.task_id)
        except Exception as e:
            # this task fails
            print('Fail to processing task', task.task_id, 'Error: ', e)
            task.status = 'failed'
            task.update_to_db()
            return


if __name__ == '__main__':
    import json
    config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    config_path = os.path.join(config_path, 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    t = TaskMonitor(**config)
    t.start()

