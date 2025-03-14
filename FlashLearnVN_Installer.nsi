; FlashLearnVN Installer Script
; Tạo bởi NSIS

; Định nghĩa các hằng số
!define APPNAME "FlashLearnVN"
!define COMPANYNAME "FlashLearnVN"
!define DESCRIPTION "Ứng dụng học từ vựng tiếng Anh"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

; Các tùy chọn chung
!include "MUI2.nsh"
!include "FileFunc.nsh"

; Tên bộ cài đặt
Name "${APPNAME}"
OutFile "${APPNAME}_Setup.exe"

; Thư mục cài đặt mặc định
InstallDir "$PROGRAMFILES\${APPNAME}"

; Yêu cầu quyền admin
RequestExecutionLevel admin

; Hiển thị thông tin chi tiết trong quá trình cài đặt
ShowInstDetails show
ShowUninstDetails show

; Thiết lập giao diện
!define MUI_ICON "dist\FlashLearnVN\ui\images\logo.ico"
!define MUI_UNICON "dist\FlashLearnVN\ui\images\logo.ico"

; Các trang cài đặt
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Các trang gỡ cài đặt
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Ngôn ngữ
!insertmacro MUI_LANGUAGE "Vietnamese"

; Phần cài đặt
Section "Cài đặt ${APPNAME}" SecInstall
    SetOutPath "$INSTDIR"
    
    ; Sao chép tất cả các file từ thư mục dist/FlashLearnVN
    File /r "dist\FlashLearnVN\*.*"
    
    ; Tạo thư mục dữ liệu
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\data\categories"
    CreateDirectory "$INSTDIR\data\categories\Chung"
    
    ; Tạo shortcut trong Start Menu
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\FlashLearnVN.exe" "" "$INSTDIR\ui\images\logo.ico"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Gỡ cài đặt.lnk" "$INSTDIR\uninstall.exe"
    
    ; Tạo shortcut trên Desktop
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\FlashLearnVN.exe" "" "$INSTDIR\ui\images\logo.ico"
    
    ; Tạo uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Thêm thông tin vào registry để hiển thị trong Control Panel
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\ui\images\logo.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "$\"${COMPANYNAME}$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}$\""
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    
    ; Tính kích thước cài đặt
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
SectionEnd

; Phần gỡ cài đặt
Section "Uninstall"
    ; Xóa shortcut
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Gỡ cài đặt.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Xóa các file cài đặt
    RMDir /r "$INSTDIR\*.*"
    RMDir "$INSTDIR"
    
    ; Xóa thông tin registry
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd 