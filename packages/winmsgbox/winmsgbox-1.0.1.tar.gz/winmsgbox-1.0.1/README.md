# winmsgbox

A simple wrapper of Windows' [MessageBoxW function](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxw) written in Python to display message boxes.

## Features

- Display native Windows message boxes from Python
- Choose button sets, icons, default buttons, modality, and more
- Typed constants for easy configuration

## Requirements

- Windows OS
- Python 3.x

## Installation

Simply install using `pip install winmsgbox`

## Usage

```python
from winmsgbox import MessageBox, Buttons, Icon, DefaultButton, Modal, Flags, Response

result = MessageBox(
    title="Hello",
    text="This is a message box.",
    buttons=Buttons.OkCancel,
    icon=Icon.Information,
    defaultButton=DefaultButton.First,
    modal=Modal.ApplModal,
    flags=Flags.SetForeground
)

if result == Response.Ok:
    print("User clicked OK")
elif result == Response.Cancel:
    print("User clicked Cancel")
```

## API Reference

### MessageBox

```python
MessageBox(
    title="",
    text="",
    buttons=Buttons.Ok,
    icon=Icon.Empty,
    defaultButton=DefaultButton.First,
    modal=Modal.ApplModal,
    flags=0x00000000,
    window=0
) -> int
```
Displays a Windows message box with the specified parameters. Returns an integer corresponding to the button clicked.

### Constants

- `Buttons`: Ok, OkCancel, AbortRetryIgnore, YesNoCancel, YesNo, RetryCancel, CancelTryContinue
- `Icon`: Empty, Error, Question, Warning, Information
- `DefaultButton`: First, Second, Third, Fourth
- `Modal`: ApplModal, SystemModal, TaskModal
- `Flags`: DefaultDesktopOnly, Right, RtlReading, SetForeground, TopMost, ServiceNotification
- `Response`: Ok, Cancel, Abort, Retry, Ignore, Yes, No, TryAgain, Continue

## License

[GNU AGPL v3](LICENSE)