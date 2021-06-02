%global debug_package %{nil}
# workaround debug-id conflicts (with fx_cast)
%global _build_id_links none
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}
%global __provides_exclude_from %{_datadir}/%{name}
%global __requires_exclude_from %{_datadir}/%{name}

%global commit0 5a430c0c2221b27afe68711ac63df44cfaaea0ea
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

# Put here new versions of yarn
#https://github.com/yarnpkg/yarn/releases
%global y_ver 1.4.1

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
Version: 1.6.3
Release: 2%{?dist}
License: GPLv2
Source0: https://github.com/mi-g/vdhcoapp/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Patch:   vdhcoapp.patch
#-------------------------------------
BuildRequires: git 
BuildRequires: wget 
Requires: ffmpeg

%description
Companion application for Video DownloadHelper browser add-on.

%prep
%autosetup -n %{name}-%{commit0} -p1

%build

# get yarn
wget -c https://github.com/yarnpkg/yarn/releases/download/v%{y_ver}/yarn-v%{y_ver}.tar.gz
tar xmzvf yarn-v%{y_ver}.tar.gz -C ~

# activate yarn
echo "export PATH=$PATH:~/yarn-v%{y_ver}/bin/:~/yarn-v%{y_ver}/lib/" >> ~/.bashrc

# get nvm

git clone git://github.com/creationix/nvm.git ~/nvm

# activate nvm

echo "source ~/nvm/nvm.sh" >> ~/.bashrc

source ~/.bashrc
nvm install 10
nvm use 10

# Begin the build
XCFLAGS="-g -O2 -fstack-protector-strong -Wformat -Werror=format-security -D_FORTIFY_SOURCE=2" XLDFLAGS="-Wl,-z,relro"

~/yarn-v%{y_ver}/bin/yarn install
#~/yarn-v%{y_ver}/bin/yarn add brunch
#npm install

# Our Firefox multilib path
%ifarch x86_64 
sed -i 's|/usr/lib|/usr/lib64|g' gulpfile.js
sed -i 's|/usr/lib|/usr/lib64|g' app/native-autoinstall.js
sed -i 's|lib/x86_64-linux-gnu|lib64|g' converter/build-apps.sh
%endif

# We need said a npm/yarn the path of binaries already installed... 
export PATH=$PATH:/usr/bin/:$PWD/node_modules/.bin/

# Now the installation
gulp build-linux-%{platform}


%install

install -Dm755 bin/net.downloadhelper.coapp-* %{buildroot}/%{_bindir}/vdhcoapp
install -Dm644 config.json %{buildroot}/%{_datadir}/vdhcoapp/config.json

%pre

if [ -f /usr/bin/vdhcoapp ]; then
/usr/bin/vdhcoapp uninstall --system
else
echo 'New installation of vdhcoapp'
fi

%post
/usr/bin/vdhcoapp install --system


%files
%defattr(755, root, root)
%license LICENSE.txt
%{_bindir}/%{name}
%{_datadir}/%{name}/config.json

%changelog

* Fri May 28 2021 David Va <davidva AT tuta DOT io> - 1.6.3-2
- Updated to 1.6.3

* Sat Mar 20 2021 David Va <davidva AT tuta DOT io> - 1.6.1-2
- Updated to 1.6.1

* Sun Dec 20 2020 David Va <davidva AT tuta DOT io> - 1.6.0-2
- Updated to 1.6.0

* Wed Apr 15 2020 David Va <davidva AT tuta DOT io> - 1.5.0-2
- Updated to 1.5.0

* Wed Mar 11 2020 David Va <davidva AT tuta DOT io> - 1.4.0-2
- Updated to 1.4.0

* Fri Jun 21 2019 David Va <davidva AT tuta DOT io> - 1.3.0-2
- Updated to current commit

* Thu Jun 20 2019 David Va <davidva AT tuta DOT io> - 1.3.0-1
- Updated to 1.3.0

* Wed Jul 04 2018 David Va <davidva AT tuta DOT io> - 1.2.4-1
- Updated to 1.2.4

* Thu Jun 14 2018 David Va <davidva AT tuta DOT io> - 1.2.3-1
- Updated to 1.2.3

* Wed Jun 06 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.2.2-1
- Updated to 1.2.2

* Mon May 28 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.2.1-1
- Updated to 1.2.1

* Wed May 16 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.2.0-1
- Updated to 1.2.0

* Thu Feb 01 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.3-1
- Updated to 1.1.3

* Thu Jan 25 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.2-2
- Rebuilt for Firefox

* Thu Jan 11 2018 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.2-1
- Updated to 1.1.2-1

* Mon Dec 18 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.1-1
- Updated to 1.1.1-1

* Thu Dec 14 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1.1.0-1
- initial build
