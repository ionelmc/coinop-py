FROM base/arch
RUN pacman -Sy
RUN pacman -S --noconfirm python2
ADD . ./coinop
ADD . ./coinop.egg-info
ADD . ./setup.py
RUN python setup.py develop
