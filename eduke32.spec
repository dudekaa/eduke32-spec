# These lines are targets for Jenkins sed commands
%global commit e35219148c8f3b0547408c1c00909158f7ec5c9d
%global date 20240620

# Helper macros (do not edit these manually)
%global shortcommit %(c=%{commit}; echo ${c:0:8})

%global debug_package %{nil}

Name:           eduke32
Version:        0.1
# Release format: <build>.<date>g<hash>
Release:        5.%{date}g%{shortcommit}%{?dist}
Summary:        The unofficial build of official EDuke32 repository

Group:          Games
License:        GPLv2
URL:            https://voidpoint.io/terminx/eduke32/
# https://voidpoint.io/terminx/eduke32/-/tree/e35219148c8f3b0547408c1c00909158f7ec5c9d
Source0:        %{url}-/archive/%{commit}/eduke32-%{commit}.zip
Patch0:         eduke32.desktop.patch
Patch1:         mapster32.desktop.patch

BuildRequires:  make automake gcc gcc-c++ kernel-devel
BuildRequires:  SDL2-devel
BuildRequires:  flac-devel
BuildRequires:  libogg-devel
BuildRequires:  libvpx-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  libatomic
BuildRequires:  desktop-file-utils
Requires:       SDL2
Requires:       flac-libs
Requires:       libogg
Requires:       libvpx
Requires:       alsa-lib
Requires:       libatomic

%description
The unofficial build of official EDuke32 Git repository: home to the source code to EDuke32, Ion Fury, and related projects based on the Build Engine.


%package mapster32
Summary:        EDuke32 map editor
%description mapster32
EDuke32 map editor


%prep
%setup -n %{name}-%{commit} -q
%patch -P 0 -p0
%patch -P 1 -p0


%build
# https://voidpoint.io/terminx/eduke32/-/issues/269
make -f GNUmakefile


%install
rm -rf $RPM_BUILD_ROOT
# % make_install
mkdir -p $RPM_BUILD_ROOT/usr/bin
install -p ./%{name} $RPM_BUILD_ROOT/usr/bin/%{name}
install -p ./mapster32 $RPM_BUILD_ROOT/usr/bin/mapster32
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
install -p -m 0644 ./%{name}.desktop $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop
desktop-file-validate $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop
install -p -m 0644 ./mapster32.desktop $RPM_BUILD_ROOT/usr/share/applications/mapster32.desktop
desktop-file-validate $RPM_BUILD_ROOT/usr/share/applications/mapster32.desktop


%files
/usr/bin/%{name}
/usr/share/applications/%{name}.desktop

%files mapster32
/usr/bin/mapster32
/usr/share/applications/mapster32.desktop

%changelog
* Thu Jun 20 2024 Arnošt Dudek <arnost@arnostdudek.cz> - 0.1-4.20240620ge35219148
- rebuilt

* Thu Jan 11 2024 Arnošt Dudek <arnost@arnostdudek.cz> - 0.1-3.20240104g842047589
- separate eduke32 and mapster32 binaries

* Thu Jan 04 2024 Arnošt Dudek <arnost@arnostdudek.cz> - 0.1-2.20240104g842047589
- disable concurent builds
- fix .dekstop files rights
- force "x11" SDL backend

* Thu Jan 04 2024 Arnošt Dudek <arnost@arnostdudek.cz> - 0.1-1.20240104g842047589
- initial build
