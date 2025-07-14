# TODO:
# - fix kernel module build
# - package device in static dev package (if major,minor is static)
# - build and package libraries/ and lang/ contents
#
# Conditional build:
%bcond_with	kernel		# build kernel module (FIXME)
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	userspace	# don't build userspace packages
#
Summary:	MidiShare - a real-time operating system for musical applications
Summary(pl.UTF-8):	MidiShare - system operacyjny czasu rzeczywistego dla aplikacji muzycznych
Name:		midishare
Version:	1.93
%define	snap	20100924
Release:	1.%{snap}.1
License:	LGPL v2
Group:		Applications/Sound
# no packaged sources available for 1.93 release - so use git snapshot
#Source0:	http://downloads.sourceforge.net/midishare/%{name}-%{version}-src.tgz
# git clone git://midishare.git.sourceforge.net/gitroot/midishare/midishare midishare
Source0:	%{name}-%{snap}.tar.xz
# Source0-md5:	51a1a061d66ec1bd4fda718091cb430a
Patch0:		%{name}-ulong.patch
Patch1:		%{name}-kernelsrc.patch
Patch2:		%{name}-link.patch
Patch3:		%{name}-install.patch
Patch4:		%{name}-opt.patch
URL:		http://midishare.sourceforge.net/
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%if %{with kernel}
BuildRequires:	kernel%{_alt_kernel}-headers
BuildRequires:	kernel%{_alt_kernel}-module-build
BuildRequires:	%{kgcc_package}
%endif
%if %{with userspace}
BuildRequires:	alsa-lib-devel
BuildRequires:	gtk+2-devel >= 2.0
BuildRequires:	libstdc++-devel
BuildRequires:	pkgconfig
%endif
Requires:	%{name}-libs = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MidiShare has been designed in 1989 in response to problems commonly
met in the development of realtime music software. It provides high
level services to developers and ensures platform independance since
it currently supports GNU/Linux, MacOS X and Windows.

%description -l pl.UTF-8
MidiShare został zaprojektowany w 1989 roku w odpowiedzi na problemy
powszechnie spotykane przy tworzeniu oprogramowania muzycznego czasu
rzeczywistego. Zapewnia programistom wysokopoziomowe usługi oraz
niezależność od platformy - obecnie obsługuje systemy GNU/Linux, Mac
OS X oraz Windows.

%package gui
Summary:	GTK+ based MidiShare GUI applications
Summary(pl.UTF-8):	Oparte na GTK+ aplikacje graficzne MidiShare
Group:		X11/Applications/Sound
Requires:	%{name} = %{version}-%{release}

%description gui
GTK+ based MidiShare GUI applications.

%description gui -l pl.UTF-8
Oparte na GTK+ aplikacje graficzne MidiShare.

%package libs
Summary:	MidiShare shared library
Summary(pl.UTF-8):	Biblioteka współdzielona MidiShare
Group:		Libraries

%description libs
MidiShare shared library.

%description libs -l pl.UTF-8
Biblioteka współdzielona MidiShare.

%package devel
Summary:	Header file for MidiShare library
Summary(pl.UTF-8):	Plik nagłówkowy biblioteki MidiShare
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header file for MidiShare library.

%description devel -l pl.UTF-8
Plik nagłówkowy biblioteki MidiShare.

%package doc
Summary:	MidiShare documentation
Summary(pl.UTF-8):	Dokumentacja do MidiShare
Group:		Documentation

%description doc
MidiShare documentation.

%description doc -l pl.UTF-8
Dokumentacja do MidiShare.

%package -n kernel%{_alt_kernel}-midishare
Summary:	Linux kernel module for MidiShare system
Summary(pl.UTF-8):	Moduł jądra Linuksa dla systemu MidiShare
Release:	%{release}@%{_kernel_ver_str}
Group:		Base/Kernel
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):       %releq_kernel
%endif
Requires(post,postun):  /sbin/depmod

%description -n kernel%{_alt_kernel}-midishare
Linux kernel module for MidiShare system.

%description -n kernel%{_alt_kernel}-midishare -l pl.UTF-8
Moduł jądra Linuksa dla systemu MidiShare.

%prep
%setup -q -n %{name}
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1

%build
cd src/linux
./configure
%{__make} common \
	CC="%{__cc}" \
	COPTFLAGS="%{rpmcflags}"
%if %{with kernel}
# TODO: FIXME
%{__make} -C kernel \
	CC="%{kgcc}" \
	KERNELSRC=%{_kernelsrcdir}
%endif
%{__make} -f appls \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	COPTFLAGS="%{rpmcflags}" \
	CXXOPTFLAGS="%{rpmcxxflags}" \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
install src/linux/kernel/midishare.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir},%{_includedir},%{_mandir}/man1,%{_sysconfdir},/etc/udev/rules.d}

%{__make} -C src/linux/library install \
	DEST=$RPM_BUILD_ROOT%{_libdir}
install src/linux/Include/MidiShare.h $RPM_BUILD_ROOT%{_includedir}
install src/linux/MidiShare.conf $RPM_BUILD_ROOT%{_sysconfdir}
install src/linux/midishare-udev.rules $RPM_BUILD_ROOT/etc/udev/rules.d

%{__make} -C src/linux -f appls install \
	DEST=$RPM_BUILD_ROOT%{_bindir} \
	BIN=$RPM_BUILD_ROOT%{_bindir} \
	MAN1=$RPM_BUILD_ROOT%{_mandir}/man1
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%post	-n kernel%{_alt_kernel}-midishare
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-midishare
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc src/History.txt src/linux/{README.txt,history-linux.txt}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/MidiShare.conf
/etc/udev/rules.d/midishare-udev.rules
%attr(755,root,root) %{_bindir}/MidiConnect
%attr(755,root,root) %{_bindir}/MidiCountAppls
%attr(755,root,root) %{_bindir}/MidiGetIndAppl
%attr(755,root,root) %{_bindir}/MidiGetName
%attr(755,root,root) %{_bindir}/MidiGetNamedAppl
%attr(755,root,root) %{_bindir}/MidiGetStat
%attr(755,root,root) %{_bindir}/MidiGetTime
%attr(755,root,root) %{_bindir}/MidiGetVersion
%attr(755,root,root) %{_bindir}/MidiIsConnected
%attr(755,root,root) %{_bindir}/RadioHDServer
%attr(755,root,root) %{_bindir}/msAlsaSeq
%attr(755,root,root) %{_bindir}/msControlSignal
%attr(755,root,root) %{_bindir}/msInetDriver
%attr(755,root,root) %{_bindir}/msQuit
%attr(755,root,root) %{_bindir}/msRawDev
%attr(755,root,root) %{_bindir}/msRawMidi
%attr(755,root,root) %{_bindir}/msRawSerial
%{_mandir}/man1/MidiConnect.1*
%{_mandir}/man1/MidiCountAppls.1*
%{_mandir}/man1/MidiGetIndAppl.1*
%{_mandir}/man1/MidiGetName.1*
%{_mandir}/man1/MidiGetNamedAppl.1*
%{_mandir}/man1/MidiGetStat.1*
%{_mandir}/man1/MidiGetTime.1*
%{_mandir}/man1/MidiGetVersion.1*
%{_mandir}/man1/MidiIsConnected.1*
%{_mandir}/man1/msAlsaSeq.1*
%{_mandir}/man1/msInetDriver.1*
%{_mandir}/man1/msQuit.1*

%files gui
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/msclock
%attr(755,root,root) %{_bindir}/msconnect
%attr(755,root,root) %{_bindir}/mscontrol
%attr(755,root,root) %{_bindir}/msdisplay
%attr(755,root,root) %{_bindir}/msecho
%attr(755,root,root) %{_bindir}/mssync

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libMidiShare.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libMidiShare.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libMidiShare.so
%{_includedir}/MidiShare.h

%files doc
%defattr(644,root,root,755)
%doc doc/html
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-midishare
%defattr(755,root,root,755)
/lib/modules/%{_kernel_ver}/misc/midishare.ko*
%endif
