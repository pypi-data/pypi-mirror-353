# cashctrl
<u>Unofficial</u> python client for the [cashctrl api v1](https://app.cashctrl.com/static/help/en/api/index.html)

The goal was to make it easy, easier, easiest :smile::

```python
import cashctrl
cc=cashctrl.Client()
people=cc.person.list()
```



## Quickstart

### 1. Create role

According to the  [principle of least privilegue](https://en.wikipedia.org/wiki/Principle_of_least_privilege it is recommended to create a seperate role for the admin user.

Then you can give it the exact permission it needs:![add-role](https://raw.githubusercontent.com/blemli/cashctrl-py/main/assets/add-role.png)



### 2. Create API-User

Now we can create the api user and copy the api-key:
![add-user](https://raw.githubusercontent.com/blemli/cashctrl-py/main/assets/add-user.png)

### 3. Add credentials to your environment

Create the .env file and add your api-key, organization and language:

```bash
cp .env.example .env && open .env
```

**Make sure your .env file is in a  safe place**

### 4. have fun

```python
from cashctrl_py import CashCtrlClient
from icecream import ic

cc = CashCtrlClient()
people = cc.person.list()
ic(people)
```

## Contribute

### Submit a Pull Request

There is still much work to do 😔

If you want to contribute, please fork the repository and create a pull request.
`gh repo fork <USER>/cashctrl-py`

### Dynamic install

For development you can install this library dynamically with the following command:

```bash
pip3 install -e /path/to/cashctrl-py
```

Now you can import it normally in other projects and changes in cashctrl-py get reflected immediately in all importing projects.

### ~~Swagger~~

~~There is an unofficial [swagger.json](./swagger.json) file to help with development. You can export it into your http-client i.e. [insomnia](https://insomnia.rest/).~~ 

### IDE

The Project was developed in Vscode. You can install the recommended extensions when you first open the project:

![install-extensions](https://raw.githubusercontent.com/blemli/cashctrl-py/main/assets/install-extensions.png)

###  Upload

1. increment version number
2. upload:

```bash
./upload.sh
```

Also see: [Package Tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/#)



### .env

Make sure you don't put a .env file in the sources folder. It is dangerous because all projects that have importet cashctrl-py with `pip -e` will then use that file instead of their own...

