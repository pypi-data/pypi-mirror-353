from ctypes import windll
from platform import system
if system() != "Windows":
    raise ImportError("This library can only be used on Windows.")
    
class Buttons:
    Ok = 0x00000000
    OkCancel = 0x00000001
    AbortRetryIgnore = 0x00000002
    YesNoCancel = 0x00000003
    YesNo = 0x00000004
    RetryCancel = 0x00000005
    CancelTryContinue = 0x00000006

class Icon:
    Empty = 0x00000000
    Error = 0x00000010
    Question = 0x00000020
    Warning = 0x00000030
    Information = 0x00000040

class DefaultButton:
    First = 0x00000000
    Second = 0x00000100
    Third = 0x00000200
    Fourth = 0x00000300

class Modal:
    ApplModal = 0x00000000
    SystemModal = 0x00001000
    TaskModal = 0x00002000
    
class Flags:
    DefaultDesktopOnly = 0x00020000
    Right = 0x00080000
    RtlReading = 0x00100000
    SetForeground = 0x00010000
    TopMost = 0x00040000
    ServiceNotification = 0x00200000

class Response:
    Ok = 1
    Cancel = 2
    Abort = 3
    Retry = 4
    Ignore = 5
    Yes = 6
    No = 7
    TryAgain = 10
    Continue = 11
    
def MessageBox(title="", text="", buttons=Buttons.Ok, icon=Icon.Empty, defaultButton=DefaultButton.First, modal=Modal.ApplModal, flags=0x00000000, window=0) -> int:
    """
    Creates a message box with the specified parameters.
    Returns the integer of the button clicked by the user.
    
    :param title: The title of the message box.
    :param text: The message to display in the box.
    :param buttons: The buttons to be displayed in the box.
    :param icon: The icon to be used in the box.
    :param defaultButton: The default button to be highlighted.
    :param modal: The modality of the dialog box.
    :param flags: Any custom flags to be used.
    :param window: The handle to the owner window.
    """
    return windll.user32.MessageBoxW(window, text, title, buttons | icon | defaultButton | modal | flags)
    
__all__ = [ Buttons, Icon, DefaultButton, Modal, Flags, Response, MessageBox ]