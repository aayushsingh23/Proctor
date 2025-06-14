
# Proctor

A brief description of what this project does and who it's for

## venv setup

 1. Go to your directory
 ``` 
 cd path/to/your/project

 ```

 2. Setup python venv 
 ```
 python -m venv venv
```
3. Activate it
```
venv\Scripts\activate
```

**Note**:if it shows some authentication error of some type here. Run the following commands. This is a temporary fix.

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\venv\Scripts\Activate.ps1
```

## Backend

To run backend run the following command inside the venv

```
python app.py
```