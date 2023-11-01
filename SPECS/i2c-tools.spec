# Copyright (c) 2007 SUSE LINUX Products GmbH, Nuernberg, Germany.
# Copyright (c) 2007 Hans de Goede <j.w.r.degoede@hhs>, the Fedora project.
#
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.

%if 0%{?rhel} > 7 || 0%{?fedora} > 28
%bcond_with python2
%else
%bcond_without python2
%endif

Name:           i2c-tools
Version:        4.0
Release:        12%{?dist}
Summary:        A heterogeneous set of I2C tools for Linux
License:        GPLv2+
URL:            https://i2c.wiki.kernel.org/index.php/I2C_Tools
Source0:        https://www.kernel.org/pub/software/utils/i2c-tools/%{name}-%{version}.tar.xz
# Upstream patch
Patch0:         0001-i2c-tools-i2cbusses-Avoid-buffer-overflows-in-sysfs-.patch
# Upstream patch
Patch1:         0002-tools-i2cbusses-Check-the-return-value-of-snprintf.patch
# Upstream patch
Patch2:         0003-py-smbus-Fix-FSF-address-in-smbusmodule.c.patch
# Upstream patch fixing license headers of libi2c
Patch3:         0001-libi2c-Mention-the-correct-license-in-source-files.patch

# for /etc/udev/makedev.d resp /usr/lib/modprobe.d ownership
Requires:       udev module-init-tools
Requires:       libi2c%{?_isa} = %{version}-%{release}
BuildRequires:  perl-generators
%if %{with python2}
BuildRequires:  python2-devel
%endif
BuildRequires:  python3-devel
BuildRequires:  gcc
ExcludeArch:    s390 s390x

%description
This package contains a heterogeneous set of I2C tools for Linux: a bus
probing tool, a chip dumper, register-level access helpers, EEPROM
decoding scripts, and more.


%package eepromer
Summary:        Programs for reading / writing i2c / smbus eeproms
Requires:       libi2c%{?_isa} = %{version}-%{release}
# For the device nodes
Requires:       %{name} = %{version}-%{release}
# /usr/sbin/eeprom is Public Domain, the rest is GPLv2+
License:        GPLv2+ and Public Domain

%description eepromer
Programs for reading / writing i2c / smbus eeproms. Notice that writing the
eeproms in your system is very dangerous and is likely to render your system
unusable. Do not install, let alone use this, unless you really, _really_ know
what you are doing.

%if %{with python2}
%package -n python2-i2c-tools
%{?python_provide:%python_provide python2-i2c-tools}
Requires:       libi2c%{?_isa} = %{version}-%{release}
# Remove before F30
Provides: %{name}-python = %{version}-%{release}
Provides: %{name}-python%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-python < 4.0-4
Summary:        Python 2 bindings for Linux SMBus access through i2c-dev
License:        GPLv2

%description -n python2-i2c-tools
Python 2 bindings for Linux SMBus access through i2c-dev
%endif

%package -n python3-i2c-tools
%{?python_provide:%python_provide python3-i2c-tools}
Requires:       libi2c%{?_isa} = %{version}-%{release}
%if %{without python2}
# Remove before F30
Obsoletes: %{name}-python < 4.0-4
# Remove before F31
Obsoletes: python2-i2c-tools < 4.0-5
%endif
Summary:        Python 3 bindings for Linux SMBus access through i2c-dev
License:        GPLv2

%description -n python3-i2c-tools
Python 3 bindings for Linux SMBus access through i2c-dev

%package perl
Summary:        i2c tools written in Perl
License:        GPLv2+
Requires:       libi2c%{?_isa} = %{version}-%{release}

%description perl
A collection of tools written in perl for use with i2c devices.

%package -n libi2c
Summary:        I2C/SMBus bus access library
License:        LGPLv2+

%description -n libi2c
libi2c offers a way for applications to interact with the devices
connected to the I2C or SMBus buses of the system.

%package -n libi2c-devel
Summary:        Development files for the I2C library
License:        LGPLv2+
Requires:       libi2c%{?_isa} = %{version}-%{release}
# Remove in F30
Obsoletes:      i2c-tools-devel < 4.0-1

%description -n libi2c-devel
%{summary}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
make CFLAGS="$RPM_OPT_FLAGS" LDFLAGS="$RPM_LD_FLAGS" BUILD_STATIC_LIB=0 EXTRA=eeprog
pushd eepromer
make CFLAGS="$RPM_OPT_FLAGS -I../include" LDFLAGS="$RPM_LD_FLAGS"
popd
pushd py-smbus
%if %{with python2}
CFLAGS="$RPM_OPT_FLAGS -I../include" LDFLAGS="$RPM_LD_FLAGS" \
  %{__python2} setup.py build -b build-py2
%endif
CFLAGS="$RPM_OPT_FLAGS -I../include" LDFLAGS="$RPM_LD_FLAGS" \
  %{__python3} setup.py build -b build-py3
popd


%install
make install DESTDIR=$RPM_BUILD_ROOT prefix=%{_prefix} BUILD_STATIC_LIB=0 \
  EXTRA=eeprog libdir=%{_libdir}
install -m 755 eepromer/{eepromer,eeprom} \
  $RPM_BUILD_ROOT%{_sbindir}
install -m 644 eepromer/{eepromer,eeprom}.8 \
  $RPM_BUILD_ROOT%{_mandir}/man8
pushd py-smbus
%if %{with python2}
%{__python2} setup.py build -b build-py2 install --skip-build --root=$RPM_BUILD_ROOT
%endif
%{__python3} setup.py build -b build-py3 install --skip-build --root=$RPM_BUILD_ROOT
popd
# cleanup
rm -f $RPM_BUILD_ROOT%{_bindir}/decode-edid.pl
# Remove unpleasant DDC tools.  KMS already exposes the EDID block in sysfs,
# and edid-decode is a more complete tool than decode-edid.
rm -f $RPM_BUILD_ROOT%{_bindir}/{ddcmon,decode-edid}
# for i2c-dev ondemand loading through kmod
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/modprobe.d
echo "alias char-major-89-* i2c-dev" > \
  $RPM_BUILD_ROOT%{_prefix}/lib/modprobe.d/i2c-dev.conf
# for /dev/i2c-# creation (which are needed for kmod i2c-dev autoloading)
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/udev/makedev.d
for (( i = 0 ; i < 8 ; i++ )) do
  echo "i2c-$i" >> $RPM_BUILD_ROOT%{_sysconfdir}/udev/makedev.d/99-i2c-dev.nodes
done

# auto-load i2c-dev after reboot
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/modules-load.d
echo 'i2c-dev' > $RPM_BUILD_ROOT%{_prefix}/lib/modules-load.d/%{name}.conf


%post
# load i2c-dev after the first install
if [ "$1" = 1 ] ; then
  /usr/sbin/modprobe i2c-dev
fi
exit 0

%ldconfig_post -n libi2c
%ldconfig_postun -n libi2c


%files
%doc CHANGES COPYING README
%config(noreplace) %{_prefix}/lib/modprobe.d/i2c-dev.conf
%config(noreplace) %{_sysconfdir}/udev/makedev.d/99-i2c-dev.nodes
%{_sbindir}/*
%exclude %{_sbindir}/eepro*
%exclude %{_sbindir}/i2c-stub*
%{_mandir}/man8/*.8.gz
%exclude %{_mandir}/man8/eepro*
%exclude %{_mandir}/man8/i2c-stub-from-dump.8.gz
%{_prefix}/lib/modules-load.d/%{name}.conf

%files eepromer
%doc eepromer/README*
%doc eeprog/README.eeprog
%{_sbindir}/eepro*
%{_mandir}/man8/eepro*.8.gz

%if %{with python2}
%files -n python2-i2c-tools
%doc py-smbus/README
%{python2_sitearch}/*
%endif

%files -n python3-i2c-tools
%doc py-smbus/README
%{python3_sitearch}/*

%files perl
%doc eeprom/README
%{_bindir}/decode-*
%{_sbindir}/i2c-stub*
%{_mandir}/man1/decode-*.1.gz
%{_mandir}/man8/i2c-stub-from-dump.8.gz

%files -n libi2c
%doc COPYING.LGPL
%{_libdir}/libi2c.so.*

%files -n libi2c-devel
%dir %{_includedir}/i2c
%{_includedir}/i2c/smbus.h
%{_libdir}/libi2c.so


%changelog
* Wed Dec 05 2018 Ondřej Lysoněk <olysonek@redhat.com> - 4.0-12
- Use versioned dependency on libi2c in subpackages
- Resolves: rhbz#1650317

* Thu Nov 15 2018 Ondřej Lysoněk <olysonek@redhat.com> - 4.0-11
- Ship modprobe.d files in /usr/lib/modprobe.d
- Resolves: rhbz#1649735

* Fri Aug 03 2018 Ondřej Lysoněk <olysonek@redhat.com> - 4.0-10
- Add upstream patch fixing libi2c license headers

* Tue Jul 31 2018 Ondřej Lysoněk <olysonek@redhat.com> - 4.0-9
- Corrected the License tags

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 29 2018 Adam Jackson <ajax@redhat.com> - 4.0-7
- Use ldconfig scriptlets

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 4.0-6
- Rebuilt for Python 3.7

* Thu Mar 22 2018 Ondřej Lysoněk <olysonek@redhat.com> - 4.0-5
- Don't build Python 2 subpackage on EL > 7 and Fedora > 28

* Mon Feb 19 2018 Ondřej Lysoněk <olysonek@redhat.com> - 4.0-4
- Add gcc to BuildRequires

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Feb  1 2018 Florian Weimer <fweimer@redhat.com> - 4.0-2
- Build with linker flags from redhat-rpm-config

* Tue Nov 21 2017 Ondřej Lysoněk <olysonek@redhat.com> - 4.0-1
- New version
- Dropped i2c-tools-devel, introduced libi2c, libi2c-devel

* Sat Oct 7 2017 Troy Curtis, Jr <troycurtisjr@gmail.com> - 3.1.2-7
- Add Python3 subpackage.

* Sun Aug 20 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.1.2-6
- Add Provides for the old name without %%_isa

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 3.1.2-5
- Python 2 binary package renamed to python2-i2c-tools
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 20 2017 Ondřej Lysoněk <olysonek@redhat.com> - 3.1.2-2
- Provide i2c-dev.h in /usr/include/i2c-tools/
- Resolves: rhbz#1288823
- Dropped Group: tags as per https://fedoraproject.org/wiki/Packaging:Guidelines#Tags_and_Sections

* Wed Jul 19 2017 Ondřej Lysoněk <olysonek@redhat.com> - 3.1.2-1
- New version
- Updated upstream and source code URL
- Dropped patches accepted by upstream

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.1.0-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-17
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.1.0-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Oct 08 2015 Jaromir Capik <jcapik@redhat.com> - 3.1.0-15
- Adding i2c-dev auto-load in th %%post and modules-load.d (#913203)

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Oct 9  2013 Peter Robinson <pbrobinson@fedoraproject.org> 3.1.0-11
- Split out perl tools to a separate subpackage

* Fri Oct 04 2013 Jaromir Capik <jcapik@redhat.com> - 3.1.0-10
- Making the decode-* man pages installable with Makefile

* Thu Oct 03 2013 Jaromir Capik <jcapik@redhat.com> - 3.1.0-9
- Introducing man pages for decode-* binaries
- Cleaning the spec

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 3.1.0-7
- Perl 5.18 rebuild

* Wed Jul 03 2013 Jaromir Capik <jcapik@redhat.com> - 3.1.0-6
- Installing the man pages and putting them in the files section

* Wed Jul 03 2013 Jaromir Capik <jcapik@redhat.com> - 3.1.0-5
- Introducing man pages for binaries in the eepromer subpackage
- Introducing -r switch in the i2cset help

* Sat Jun  1 2013 Henrik Nordstrom <henrik@henriknordstrom.net> - 3.1.0-4
- Package python interface

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Feb 20 2012 Adam Jackson <ajax@redhat.com> 3.1.0-1
- i2c-tools 3.1.0

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Jul 05 2011 Adam Jackson <ajax@redhat.com> 3.0.3-1
- i2c-tools 3.0.3

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Apr 13 2009 Adam Jackson <ajax@redhat.com> 3.0.2-3
- mv /etc/modprobe.d/i2c-dev /etc/modprobe.d/i2c-dev.conf (#495455)

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Dec 11 2008 Adam Jackson <ajax@redhat.com> 3.0.2-1
- i2c-tools 3.0.2

* Wed Mar  5 2008 Hans de Goede <j.w.r.degoede@hhs.nl> 3.0.0-3
- Change /dev/i2c-# creation from /lib/udev/devices to /etc/udev/makedev.d
  usage
- Add an /etc/modprobe.d/i2c-dev file to work around bug 380971

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.0.0-2
- Autorebuild for GCC 4.3

* Tue Nov 13 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 3.0.0-1
- Initial Fedora package, based on Suse specfile

* Mon Oct 15 2007 - jdelvare@suse.de
- Initial release.
