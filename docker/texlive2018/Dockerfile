FROM ubuntu:18.04

# install texlive
RUN apt-get update && apt-get install -y wget perl libfontconfig locales \
    && apt-get clean \
    && wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
    && mkdir /install-tl-unx \
    && tar -xvf install-tl-unx.tar.gz -C /install-tl-unx --strip-components=1

RUN echo "selected_scheme scheme-full" >> /install-tl-unx/texlive.profile \
    && /install-tl-unx/install-tl -profile /install-tl-unx/texlive.profile \
    && rm -r /install-tl-unx \
    && rm install-tl-unx.tar.gz
ENV PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/texlive/2018/bin/x86_64-linux/:$PATH
WORKDIR /usr/local/texlive/2018/bin/x86_64-linux
RUN ./tlmgr install latexmk \
    && ./tlmgr install texcount

# set the locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
