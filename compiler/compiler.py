# coding: utf-8

import os
import time
import base64
import shutil
import subprocess
import multiprocessing
from string import Template

from models.users import User
from models.pdfs import PDF
from models.tasks import Task


class LatexCompiler(multiprocessing.Process):

    """Compiler for compiling LaTex documents.

        Finish task object will have a `pdf_b64` attribute.

    """

    def __init__(self, structure_dir, template_configs, temp_dir, compile_cmd, compile_timeout, task_queue, result_queue, name="Compiler"):
        multiprocessing.Process.__init__(self, name=name)
        self.structure_dir = structure_dir
        self.template_configs = template_configs
        # converting to real path
        self.temp_dir = os.path.realpath(temp_dir)
        self.compile_cmd = compile_cmd
        self.compile_timeout = compile_timeout
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            task = self.task_queue.get()
            print(self.name, 'starts', 'processing task:', task.task_id)
            # create temp directory
            compile_tmp_dir = os.path.join(self.temp_dir, task.task_id)
            os.mkdir(compile_tmp_dir)
            filename = task.task_id + '.tex'
            filepath = os.path.join(compile_tmp_dir, filename)
            pdfname = task.task_id + '.pdf'
            pdfpath = os.path.join(compile_tmp_dir, pdfname)
            # get structure document path
            structure = self.template_configs[task.template]['structure']
            structure_path = os.path.join(self.structure_dir, structure)
            with open(structure_path, 'r') as f:
                structure_t = Template(f.read())
            # get template's arguments
            args = task.args
            print(args)
            sub_dict = dict(documentclass=task.template, body=task.body)
            if args:
                for arg, value in args.items():
                    sub_dict[arg] = value
            latex = structure_t.substitute(sub_dict)
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
            try:
                command = self.compile_cmd.format(
                    filepath=filepath,
                    outdir=compile_tmp_dir
                )
                subprocess.run(
                    command,
                    shell=True,
                    timeout=self.compile_timeout
                )
                # read pdf content and parsed into b64 string
                with open(pdfpath, 'rb') as f:
                    pdf_content = f.read()
                pdf_b64 = base64.b64encode(pdf_content).decode('utf-8')
                # put into result queue
                task.pdf_b64 = pdf_b64
                self.result_queue.put(task)
            except subprocess.TimeoutExpired as e:
                print("Compile timeout: ", e)
            finally:
                # cleanup tmp files
                shutil.rmtree(compile_tmp_dir)
                print(self.name, 'end', 'processing task:', task.task_id)


class TaskMonitor:

    """Monitor of processing uncompiled tasks in db."""

    def __init__(self, structure_dir='', templates={},
                 compile_cmd=None, compile_timeout=300,
                 compile_tmp_dir='compiler-tmp',
                 compiler_number=None, db_scan_interval=1, **other):
        self.name = self.__class__.__name__
        # compiler settings
        if not structure_dir:
            structure_dir = os.path.dirname(os.path.realpath(__file__))
            structure_dir = os.path.join(structure_dir, 'structures')
        self.structure_dir = structure_dir
        self.template_configs = templates
        if not compiler_number:
            compiler_number = multiprocessing.cpu_count()
        self.compiler_number = compiler_number
        if not compile_cmd:
            raise ValueError("no compile command provided.")
        self.compile_cmd = compile_cmd
        self.compile_timeout = compile_timeout
        self.compile_tmp_dir = compile_tmp_dir
        if not os.path.exists(self.compile_tmp_dir):
            os.mkdir(self.compile_tmp_dir)
        # other settings
        self.db_scan_interval = db_scan_interval
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        # child processes
        self.compilers = None

    def scan(self):
        results = Task.find_all()
        compile_tasks = []
        for result in results:
            task = Task(**result)
            if task.status == 'new':
                compile_tasks.append(task)
                task.status = 'compiling'
                task.update_to_db()
            elif task.status == "compiling":
                pass
            elif task.status == "finished":
                pass
            else:
                print("unknown task's status:", task.status)
        return compile_tasks

    def process_result(self, task_result):
        print(self.name, 'starts', 'processing result:', task_result.task_id)
        # get pdf b64 string and put into db
        pdf_b64 = task_result.pdf_b64
        compiled_time = str(int(time.time()))
        pdf = PDF(data=pdf_b64, compiled_time=compiled_time)
        pdf.create_in_db()
        user = User(user_id=task_result.user_id)
        user.load_from_db()
        user.compiled_pdfs.append(pdf.pdf_id)
        user.update_to_db()
        # update task into task
        task_result.status = "finished"
        task_result.update_to_db()
        # delete task.Canceled, task will be deleted by client's request
        # task_result.delete_in_db()
        print(self.name, 'ends', 'processing result:', task_result.task_id)

    def start(self):
        print('Creating {} latex compilers'.format(self.compiler_number))
        self.compilers = [
            LatexCompiler(
                self.structure_dir,
                self.template_configs,
                self.compile_tmp_dir,
                self.compile_cmd,
                self.compile_timeout,
                self.task_queue,
                self.result_queue,
                name='Compiler '+str(i))
            for i in range(self.compiler_number)
        ]
        for c in self.compilers:
            c.start()

        while True:
            # scan tasks in db and put into task queue
            compile_tasks = self.scan()
            for task in compile_tasks:
                self.task_queue.put(task)
            # process finished tasks' result
            for check_time in range(self.compiler_number):
                try:
                    task_result = self.result_queue.get(block=False)
                    self.process_result(task_result)
                except multiprocessing.queues.Empty:
                    pass
            # monitor result queue and task queue
            print('Task queue size:', self.task_queue.qsize())
            print('Result queue size:', self.result_queue.qsize())
            time.sleep(self.db_scan_interval)


if __name__ == '__main__':
    import json
    config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    config_path = os.path.join(config_path, 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    t = TaskMonitor(**config)
    t.start()

