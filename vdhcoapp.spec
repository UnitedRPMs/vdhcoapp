%{?nodejs_find_provides_and_requires}
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%global commit0 9989b1ada04d3e51135ae2b5de6a42786e97abc4
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

# Put here new versions of yarn
#https://github.com/yarnpkg/yarn/releases
%global y_ver 1.3.2

# We need said to gulp our Machine
%ifarch x86_64 
%global platform 64
%else
%global platform 32
%endif

Name: vdhcoapp
Summary: Companion application for Video DownloadHelper browser add-on 
Group: Applications/Internet
URL: https://github.com/mi-g/vdhcoapp
Version: 1.1.0
Release: 1%{?gver}%{?dist}
License: GPLv2
Source0: https://github.com/mi-g/vdhcoapp/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Source1: vdhcoapp-snapshot
Patch:   vdhcoapp.patch
#-------------------------------------
BuildRequires: git 
BuildRequires: wget
Requires: ffmpeg

%description
Companion application for Video DownloadHelper browser add-on.

%prep

%{S:1} -c %{commit0}
%setup -T -D -n %{name}-%{shortcommit0} 
%patch -p1

%build

# get yarn
wget -c https://github.com/yarnpkg/yarn/releases/download/v%{y_ver}/yarn-v%{y_ver}.tar.gz
tar xmzvf yarn-v1.3.2.tar.gz -C ~

# activate yarn
echo "export PATH=$PATH:~/yarn-v%{y_ver}/bin/:~/yarn-v%{y_ver}/lib/" >> ~/.bashrc

# get nvm

git clone git://github.com/creationix/nvm.git ~/nvm

# activate nvm

echo "source ~/nvm/nvm.sh" >> ~/.bashrc

source ~/.bashrc
nvm install 7
nvm use 7

# Begin the build
XCFLAGS="-g -O2 -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2" XLDFLAGS="-Wl,-z,relro"

~/yarn-v%{y_ver}/bin/yarn install

# Our Firefox multilib path
%ifarch x86_64 
sed -i 's|/usr/lib|/usr/lib64|g' gulpfile.js
sed -i 's|/usr/lib|/usr/lib64|g' app/native-autoinstall.js
sed -i 's|/usr/lib|/usr/lib64|g' assets/setup-linux-system.sh.ejs
%endif

# We need said a npm/yarn the path of binaries already installed... 
export PATH=$PATH:/usr/bin/:$PWD/node_modules/.bin/

# Now the installation
gulp build-linux-%{platform}


%install

install -Dm755 bin/net.downloadhelper.coapp-* %{buildroot}/%{_bindir}/vdhcoapp
install -Dm644 config.json %{buildroot}/%{_datadir}/vdhcoapp/config.json

%post
/usr/bin/vdhcoapp uninstall --system
/usr/bin/vdhcoapp install --system

%preun
/usr/bin/vdhcoapp uninstall --system

%files
%defattr(755, root, root)
%license LICENSE.txt
%{_bindir}/%{name}
%{_datadir}/%{name}/config.json

%changelog

* Thu Dec 14 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.0-1
- initial build
