#!/usr/bin/env python
# -*- encoding: utf-8 -*-


__author__ = 'andyguo'


class OiioBaseStream(object):
    _input_count = 1
    _priority = -1
    _name = ''

    def __init__(self):
        self._inputs = []
        self._value = ''
        self._begin = None
        for x in range(self._input_count):
            self._inputs.append(None)

    def can_set_inputs(self):
        return self.__class__._input_count > 0

    def validate(self, stream, index):
        assert index < self.__class__._input_count
        assert isinstance(stream, OiioBaseStream)

    def set_input(self, stream, index):
        if self.can_set_inputs():
            self.validate(stream, index)
            self._inputs[index] = stream
            return True
        else:
            return False

    def request(self):
        self._value = ''
        for x in self._inputs:
            if x is not None:
                self._value += x.cmd()

    def combine(self):
        self._value += ''

    def cmd(self):
        self.request()
        self.combine()
        return self._value

    def run(self):
        import subprocess
        import time
        import select
        from dayu_path import DayuPath

        self.progress = {'render_frame': None, 'render_fps': None, 'render_speed': None, 'elapse_time': None}

        shell_cmd = subprocess.Popen(self.cmd(),
                                     bufsize=0,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True)

        output_file = DayuPath(self.filename)
        start_time = time.time()
        maybe_halt = 0
        current_frame = prev_frame = None
        while True:
            if shell_cmd.poll() is not None:
                break

            rs, ws, es = select.select([shell_cmd.stdout.fileno()], [], [], 1)
            render_files = sorted((x for x in output_file.parent.listdir() if '.temp' not in x),
                                  key=lambda f: f.ctime())
            if render_files:
                last_file = render_files[-1]
                current_frame = last_file.frame
                if current_frame:
                    self.progress['elapse_time'] = time.time() - start_time
                    self.progress['render_frame'] = current_frame
                    self.progress['render_fps'] = 0.0 if (prev_frame is None) else (current_frame - prev_frame)
                    prev_frame = current_frame

                    if current_frame == self.end:
                        maybe_halt += 1
                        if maybe_halt > 3:
                            print 'finish, but halt'
                            break

            yield self.progress

        yield (shell_cmd.returncode, shell_cmd.communicate()[0])

    def __rshift__(self, other):
        assert isinstance(other, OiioBaseStream)
        assert self.__class__._priority <= other.__class__._priority
        if other._begin is None:
            other.set_input(self, 0)
        else:
            other._begin.set_input(self, 0)
        other._begin = self._begin if self._begin else self

        return other


class GlobalStream(OiioBaseStream):
    _input_count = 1
    _priority = 10


class InputStream(OiioBaseStream):
    _input_count = 1
    _priority = 20


class FilterStream(OiioBaseStream):
    _priority = 30
    pass


class UnaryFilterStream(FilterStream):
    _input_count = 1
    _name = ''


class BinaryFilterStream(FilterStream):
    _input_count = 2
    _name = ''


class MultipleFilterStream(FilterStream):
    _input_count = 1
    _name = ''

    def __init__(self, list_of_streams):
        super(MultipleFilterStream, self).__init__()
        self._inputs = list_of_streams

    def can_set_inputs(self):
        return True

    def validate(self, stream, index):
        return True

    def set_input(self, stream, index):
        self._inputs.insert(index, stream)


class CodecStream(OiioBaseStream):
    _priority = 40


class OutputStream(OiioBaseStream):
    _priority = 50
