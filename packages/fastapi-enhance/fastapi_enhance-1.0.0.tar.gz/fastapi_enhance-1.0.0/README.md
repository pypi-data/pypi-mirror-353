# FastAPI Enhance

---

**Source Code**: <a href="https://github.com/hgz1989/fastapi-enhance" target="_blank">https://github.com/hgz1989/fastapi-enhance</a>

---

Installation
------------

``pip install fastapi-enhance``


Hello World Example
-------------------

.. code:: python

    from fastapi import FastAPI
    from fastapi-enhance import enhance

    app = FastAPI(title='Hello World Example')
    app.enhance() # 或enhance(app)


    @app.get('/')
    async def index():
        return {'hello': 'world'}

    if __name__ == '__main__':
        import uvicorn

        uvicorn.run(app)