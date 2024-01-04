%global insidedir eduke32-84204758904b33787220400501f71b5b82fb9708 
%global debug_package %{nil}

Name:           eduke32
Version:        0.1
Release:        1.20240104g842047589%{?dist}
Summary:        The unofficial build of official EDuke32 repository

Group:          Games
License:        UNKOWN
URL:            https://voidpoint.io/terminx/eduke32/
# https://voidpoint.io/terminx/eduke32/-/tree/84204758904b33787220400501f71b5b82fb9708
Source0:        https://voidpoint.io/terminx/eduke32/-/archive/84204758904b33787220400501f71b5b82fb9708/eduke32-84204758904b33787220400501f71b5b82fb9708.zip
Patch0:         eduke32.desktop.patch
Patch1:         mapster32.desktop.patch

BuildRequires:  make automake gcc kernel-devel
BuildRequires:  flac-devel
BuildRequires:  desktop-file-utils

%description
The unofficial build of official EDuke32 Git repository: home to the source code to EDuke32, Ion Fury, and related projects based on the Build Engine.


%prep
# % autosetup
%setup -n %{insidedir} -q
%patch -P 0
%patch -P 1


%build
# % configure
# % make_build -f GNUmakefile
# alter default CFLAGS / CXXFLAGS
CFLAGS=`echo $CFLAGS | sed 's@\-g@\-g0@'`
CXXFLAGS=`echo $CXXFLAGS | sed 's@\-g@\-g0@'`
make %{?_smp_mflags} -f GNUmakefile


%install
rm -rf $RPM_BUILD_ROOT
# % make_install
mkdir -p $RPM_BUILD_ROOT/usr/bin
install -p ./%{name} $RPM_BUILD_ROOT/usr/bin/%{name}
install -p ./mapster32 $RPM_BUILD_ROOT/usr/bin/mapster32
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
install -p %_builddir/%{insidedir}/platform/fedora/%{name}.desktop $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop
desktop-file-validate $RPM_BUILD_ROOT/usr/share/applications/%{name}.desktop
install -p %_builddir/%{insidedir}/platform/fedora/mapster32.desktop $RPM_BUILD_ROOT/usr/share/applications/mapster32.desktop
desktop-file-validate $RPM_BUILD_ROOT/usr/share/applications/mapster32.desktop


%files
# % license add-license-file-here
# % doc add-docs-here
/usr/bin/%{name}
/usr/bin/mapster32
/usr/share/applications/%{name}.desktop
/usr/share/applications/mapster32.desktop


%changelog
* Thu Jan 04 2024 Arnošt Dudek <arnost@arnostdudek.cz> - 0.1-1.20240104g842047589
- initial build 
