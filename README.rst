dayu_oiio
=========

是OpenImageIO 中oiiotool 的python 封装。将操作转换为stream
的概念，可以帮助用户不用记忆繁杂的终端命令行，直观的生成处理代码。
OpenImageIO 是非常强力的序列帧转码工具，包括生成tx
的工具都可以直接通过OpenImageIO 实现！

准备工作
========

首先通过pip 进行安装

.. code:: python

   pip install -U dayu_oiio

然后，需要用户自行安装或者编译OpenImageIO 中的oiiotool
工具。具体的操作可以参照： https://github.com/OpenImageIO/oiio

对于mac 用户，可以比较简单，直接使用brew 进行安装即可：

.. code:: shell

   /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
   brew install openimageio

linux 用户也可以自行进行编译。windows
用户相对来说麻烦一些，需要自己按照OpenImageIO 官方手册自行编译。

使用方法
========

假设，用户希望对一套序列帧进行如下的操作：

1. 缩放
2. 使用ocio 转换色彩空间
3. 输出

那么对应的代码就非常简单：

.. code:: python

   from dayu_oiio.stream import *

   cmd = OIIO() >> \
         Input('/some/input/files.%04d.exr', start=1001, end=1008) >> \
         Resize(1920, 1080) >> \
         ColorConvert('Input - ARRI - V3 LogC (EI800) - Wide Gamut',
                      'ACES - ACEScg',
                      ocio='/some/ocio/config/file.config') >> \
         Output('/some/output/file.%04d', start=1101, end=1108)

   for _ in cmd.run():
       print cmd.progress

高级扩展
========

毕竟这里只封装了常用的 oiiotool
指令，如果用户需要使用的指令没有被封装，那么可以自己进行扩展：

.. code:: python

   from dayu_oiio.base import UnaryFilterStream

   class Multiply(UnaryFilterStream):
       _name = 'mul'    # 这里对应oiio 中的指令

       def __init__(self, multiply_value):    # 这里的参数是对应指令的参数
           super(Multiply, self).__init__()
           self.mul = multiply_value

       def combine(self)
           # 这里务必将oiio 拼接的指令加到 self._value 这个变量中
           self._value += '--{param} {mul}'.format(param=self._name,
                                                   mul=self.mul)

这样，就完成了一个multiply 操作的自定义封装。之后就可以直接使用了：

.. code:: python

   cmd = OIIO() >> \
         Input('/some/input/files.%04d.exr', start=1001, end=1008) >> \
         Multiply(1.4) >> \
         Output('/some/output/file.%04d', start=1101, end=1108)

   for _ in cmd.run():
       print cmd.progress

一些已知的问题
==============

-  由于oiiotool 的命令行工具，再输出运行指令的时候不是每行都flush
   到stdout，因此python 的subprocess
   在运行结束之前无法无阻塞的获得运行状态。 因此，只能够每隔1s
   进行扫描硬盘，来获得输出素材的进度

-  如果想要同时使用ocio 的色彩管理，那么需要在编译的时候加入opencolorIO
   的支持。（Mac 通过brew 安装的已经支持了）
