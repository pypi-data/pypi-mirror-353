#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: MArcelo Prestes
# E-mail: marcelo.prestes@simplyas.com
# Date: 2025-05-22

import re
from signal import SIGKILL, SIGTERM
import subprocess
import os
import shlex
import time

class OMX(object):
    """
    Classe para controle de reprodução de vídeos com omxplayer via subprocess (compatível com Python 2.7).
    """

    def __init__(self, video_file, omx_parameters="", start=True, duration=None):
        self.env = os.environ.copy()
        self.env["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"
        self.FNULL = open(os.devnull, 'w')
        self.video_file = video_file
        self.omx_parameters = omx_parameters
        self.cmd = self._build_command()
        self.duration = duration if duration is not None else self._get_video_duration()
        self.process = None
        subprocess.call("chvt 1", shell=True)

        if start:
            self.play()

    def _get_video_duration(self):
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                self.video_file
            ]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return float(output.strip())
        except Exception as e:
            print("Erro ao obter duração do vídeo: {}".format(e))
            return None

    def _build_command(self):
        args = ["omxplayer"]
        if self.omx_parameters:
            args += shlex.split(self.omx_parameters)
        args.append(self.video_file)
        return args

    def play(self):
        if self.is_running():
            return

        # Substituição por stop_services no lugar de killall
        # self._stop_services(['omxplayer.*{}.*'.format(self.video_file)], force_kill=True)

        # time.sleep(0.5)

        try:
            # cmd = self._build_command()
            self.process = subprocess.Popen(
                self.cmd,
                shell=False,
                env=self.env,
                stdin=self.FNULL,
                stdout=self.FNULL,
                stderr=self.FNULL
            )
        except Exception as e:
            print("Erro ao iniciar omxplayer: {}".format(e))

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def stop(self):
        if not self.is_running():
            return

        # Substituição por stop_services no lugar de kill process tree
        self._stop_services(['omxplayer.*{}.*'.format(self.video_file)], force_kill=True)

        self.process = None

    def get_duration(self):
        return self.duration

    def _stop_services(self, services, force_kill=False):
        if type(services) is list:
            for service in services:
                for process in self._get_pids():
                    if bool(re.match(r'.*{}.*'.format(service), process['cmdline'])):
                        try:
                            # print('Terminating: {} ({})'.format(service, process['pid']))
                            if force_kill == True:
                                os.kill(int(process['pid']), SIGKILL)
                            else:
                                os.kill(int(process['pid']), SIGTERM)
                        except:
                            pass
            time.sleep(1)
            try:
                os.waitpid(-1, os.WNOHANG)
            except:
                pass
        return None

    def _get_pids(self):
        pids_list = []
        for pid in [x for x in os.listdir('/proc') if x.isdigit()]:
            try:
                for line in open('/proc/{}/status'.format(pid)).readlines():
                    if line.startswith('PPid:'):
                        ppid = line.split(':')[1].strip()
                    if line.startswith('State:'):
                        status = line.split(':',1)[1].strip().split(' ')[0]
                if ppid and status:
                    data = dict()
                    data['pid'] = pid
                    data['ppid'] = ppid
                    data['status'] = status
                    data['cmdline'] = ' '.join(open('/proc/{}/cmdline'.format(pid)).read().split('\x00')[:-1])
                    pids_list.append(data)
            except:
                pass
        return pids_list
