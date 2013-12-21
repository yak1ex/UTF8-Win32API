UTF-8 Win32 API
===============

A library to provide Win32 API and CRT via UTF-8.

What you need is to include additional headers.

Motivation
----------

A character encoding is the one of the major differences for internationalization between Win32 and UNIX-ish OSes.
Most UNIX-ish OSes use UTF-8, as default, while Win32 uses UTF-16.
The difference also influences the types holding characters.
Most UNIX-ish OSes use just a ``char``` while Win32 uses ```wchar_t```.
It might become an obstacle to make internationalized softwares portable to both environments.

For example, Perl has such a limitation.
This is because most part in Perl for Win32 does not use Unicode but uses an ANSI codepage.
Of course, native Win32 Perl can handle UTF-8 as well as Perl on other environments.

```perl
use utf8;
use Encode;

say Encode::encode('utf-8', 'こんにちは、Perl');
```

However, it is not applicable if you interact with outside of Perl.

```perl
use utf8;
use Encode;

open my $fh, '>', '日本語ファイル.txt'; # BAD: Creating a file having a garbage name. Need to convert to cp932
say $fh Encode::encode('utf-8', 'こんにちは、Perl');
close $fh;
```

In contrast, the above code works as expected on Cygwin Perl.
This is because the Cygwin layer handles code conversion like as UNIX-ish OSes.
Though it is not clearly stated why there is such a limitation,
I guess it is caused by the difference between ```char``` and ```wchar_t```.

This UTF-8 Win32 API library eliminates the obstacle by providing APIs via UTF-8 ```char```.
Not only the Win32 APIs but also CRT (msvcrt) functions are provided.

Status
------

My main motivated target is Win32 Perl.
Therefore, the very limited set of APIs and CRT functions is provided currently.

Perl 5.18.1 is compilable by perl-5.18.1.patch.
You can see most of the patches in perl-5.18.1.patch add #include only and adjust make configuration.
Known regressions in Perl tests are some tests in cpan/Win32/t/Unicode.t due to explicit code conversions in Win32 module.

There are remaining TODO tasks such as a global variable environ for environment variables, temporary filename, execl in perlhost.h, FindFirstFileA and so on.

Usage for Perl compilation
--------------------------

### Prerequisites ###

- Cygwin
  - GNU make
  - Python
  - python-clang
  - w32api-headers
- Strawberry Perl

### Steps ###

This repository has a submodule. You may need to the following procedure beforehand.

```sh
git submodule init
git submodule update
```

Step.1: On Cygwin

```sh
# Making headers and sources
make clean generate
# Download perl-5.18.1.tar.gz by yourself, or the following line will do it if you have wget
# Patching Perl 5.18.1 sources
make repatch
```

Now, patched perl source is placed under the perl-5.18.1 folder.

Step.2: On CMD.EXE (Make sure StrawberryPerl is available)

```bat
:: Making libwin32u.a
dmake
cd  perl-5.18.1\win32
:: Making perl binary
dmake
```

You get a patched perl.exe as perl-5.18.1/perl.exe.
The code snippet above by the patched perl.exe produces a file having the correct filename.

Usage and internal
------------------

To be described.

Author
------

Yasutaka ATARASHI (yak_ex@mx.scn.tv)

License
-------

This software is distributed under the terms of the BSD 2-Clause License.
