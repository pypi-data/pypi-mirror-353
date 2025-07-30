⚠️ Not Production Ready ⚠️

# pyfost.adminui

[![PyPI - Version](https://img.shields.io/pypi/v/pyfost.adminui.svg)](https://pypi.org/project/pyfost.adminui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyfost.adminui.svg)](https://pypi.org/project/pyfost.adminui)

[Fost](https://fost.studio) Admin / CRUD frontend

-----

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install pyfost.adminui
```

## Usage

### Basic usage:

```python
from __future__ import annotations

from my_app import get_fastapi_app

from pyfost.adminui import Admin
from pyfost.adminui import AdminModel, Field

# Define your models and their getters:

class Author(AdminModel):
    id : int
    name: str

def get_authors()->list[Author]:
    # fetch all authors here
    ... 

class Book(AdminModel):
    id: int
    title: str
    author: Author|None = None
    
async def get_books()->list[Book]:
    # fetch all books here
    # Note: this can be async
    ... 

# Configure your admin:
admin = Admin("/book_management")
admin.add_view(Author, get_authors)
admin.add_view(Book, get_books)

# Add the admin pages to your fastapi app:
app = get_fastapi_app()
admin.add_to(app)
ui.run_with(app)

# Now run your app and navigate to the `/book_management` page.
```

### Customization

You can customize your admin pages by providing column and field renderers, by adding render methods to your models, etc...
See examples for more details.

### Examples

There are example usage in the pyfost.adminui.examples module.

You can run them with `python -m pyfost.adminui.examples.<example_name>`

Then browse to `http://0.0.0.0:8001/admin` 

## License
`pyfost.adminui` is distributed under the terms of the [GNU GPL-3.0 or later](https://www.gnu.org/licenses/gpl-3.0.en.html) license.

