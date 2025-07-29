#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# cython: language_level=3
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html
)
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles


def _custom_openapi(request: Request) -> JSONResponse:
    """
    自定义OpenAPI

    :return:JSON响应
    """
    request.app.openapi_schema = request.app.openapi()
    paths = request.app.openapi_schema.get('paths', {})
    for path_item in paths.values():
        for method_item in path_item.values():
            responses = method_item.get('responses')
            # remove 422 response, also can remove other status code
            if '422' in responses:
                responses.pop('422')
            content = {'application/json': {'schema': {'$ref': '#/components/schemas/ResponseSchema'}}}
            responses['4XX'] = {'description': 'Client Error Response', 'content': content}
            responses['5XX'] = {'description': 'Server Error Response', 'content': content}
    # 移除HTTPValidationError与ValidationError
    components = request.app.openapi_schema.get('components', {})
    schemas = components.get('schemas', {})
    schemas.pop('HTTPValidationError', None)
    schemas.pop('ValidationError', None)
    # schemas['ResponseSchema'] = ResponseSchema.model_json_schema()
    return JSONResponse(request.app.openapi_schema)


def _swagger_ui_html(request: Request) -> HTMLResponse:
    """
    SwaggerUIHTML

    :param request:请求实例
    :return:HTML响应
    """
    root_path = request.scope.get('root_path', '').rstrip('/')
    openapi_url = root_path + request.app.openapi_url
    oauth2_redirect_url = request.app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url
        oauth2_redirect_url = openapi_url.removesuffix('.json') + oauth2_redirect_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=request.app.title + ' - Swagger UI',
        swagger_js_url='/openapi-static/js/swagger-ui-bundle.js',
        swagger_css_url='/openapi-static/css/swagger-ui.css',
        swagger_favicon_url='data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9IjUxMiIgd2lkdGg9IjUxMiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJtMTI3LjcxMTA4MjUgMzQuNDUzMTM2NGMtMTcwLjI4MTQ3ODkgOTguMTY5MjA0Ny0xNzAuMjgxNDAyNiAzNDQuOTI0NTkxMSAwIDQ0My4wOTM3MTk1czM4NC4yODg5MTc1LTI1LjIwODQ3NyAzODQuMjg4OTE3NS0yMjEuNTQ2ODI1NC0yMTQuMDA3NTA3My0zMTkuNzE2MDMzOS0zODQuMjg4OTE3NS0yMjEuNTQ2ODk0MXptNDguNjYzMDQ3NyAzNzQuMTAwMTE2OGMtMTIyLjEzOTgwMSAwLTE5LjkyOTMwNi0xMzcuMzMzNTI2Ni0xMDQuNzc2MTYxMi0xMzQuOTY1NzI4OHYtMzYuNzAxMTI2MWM4MC4wMzg2NzM0IDkuOTMwNjE4My0xNS4zOTA2NTE3LTE0Ni4yMTI1NTQ5IDEwNC4xODM5ODI4LTEzMi41OTc2MjU3djI4LjQxMzc4MDJjLTY2LjY5MzQyMDQgMS41Nzg1ODI4LS4zOTQ2MDc1IDg2LjgxOTkxNTgtNjAuMzc5MjcyNSAxMjIuNTM0NDA4NiA2MC4zNzkyNzI1IDM5LjY2MDg4ODctMy4xNTcxMDQ1IDEzMC4wMzI1MzE3IDYwLjk3MTQ1MDggMTIwLjE2NjU5NTV2MzMuMTQ5Njk2M3ptLTQuMjg1ODEyMy0xMzMuNDIyMzMyOGMtMTMuNzgxMTI3OS03Ljk0NDk3NjgtMTMuNzgxMTI3OS0yNy45MTUxNzY0IDAtMzUuODYwMDc2OSAxMy43ODEwNTE2LTcuOTQ0OTkyMSAzMS4xMDA5MDY0IDIuMDQwMTE1NCAzMS4xMDA5MDY0IDE3LjkyOTk5MjdzLTE3LjMxOTg1NDggMjUuODc1LTMxLjEwMDkwNjQgMTcuOTMwMDg0MnptNzMuNTI5MTQ0MyAwYy0xMy43ODEwNjY5LTcuOTQ0OTc2OC0xMy43ODEwNjY5LTI3LjkxNTE3NjQgMC0zNS44NjAwNzY5IDEzLjc4MTA2NjktNy45NDQ5OTIxIDMxLjEwMDg5MTEgMi4wNDAxMTU0IDMxLjEwMDg5MTEgMTcuOTI5OTkyN3MtMTcuMzE5ODI0MiAyNS44NzUtMzEuMTAwODkxMSAxNy45MzAwODQyem03My41MjkxNDQyIDBjLTEzLjc4MTA2NjktNy45NDQ5NzY4LTEzLjc4MTA2NjktMjcuOTE1MTc2NCAwLTM1Ljg2MDA3NjkgMTMuNzgxMDY2OS03Ljk0NDk5MjEgMzEuMTAwOTgyNyAyLjA0MDExNTQgMzEuMTAwOTgyNyAxNy45Mjk5OTI3cy0xNy4zMTk5MTU4IDI1Ljg3NS0zMS4xMDA5ODI3IDE3LjkzMDA4NDJ6bTE2LjQ3OTMwOTEgMTMzLjQyMjMzMjh2LTMzLjE0OTY4ODdjNjQuMTI4NTcwNiA5Ljg2NTkzNjMuNTkyMTYzMS04MC41MDU3MDY4IDYwLjk3MTQzNTUtMTIwLjE2NjU5NTUtNTkuOTg0NjQ5Ny0zNS43MTQ0OTI4IDYuMzE0MTQ3OS0xMjAuOTU1ODI1OC02MC4zNzkyNzI1LTEyMi41MzQ0MDg2di0yOC40MTM3ODAyYzExOS41NzQ2NDYtMTMuNjE0OTI5MiAyNC4xNDUzMjQ3IDE0Mi41MjgyMjg4IDEwNC4xODM5OTA1IDEzMi41OTc2MjU3djM2LjcwMTEyNjFjLTg0Ljg0Njg2MjctMi4zNjc4MDU0IDE3LjM2MzY0NzYgMTM0Ljk2NTcyMTItMTA0Ljc3NjE1MzUgMTM0Ljk2NTcyMTJ6Ii8+PC9zdmc+',
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=request.app.swagger_ui_init_oauth,
        swagger_ui_parameters=request.app.swagger_ui_parameters,
    )


def _redoc_html(request: Request) -> HTMLResponse:
    """
    RedocHTML

    :param request:请求实例
    :return:HTML响应
    """
    root_path = request.scope.get('root_path', '').rstrip('/')
    openapi_url = root_path + request.app.openapi_url
    return get_redoc_html(
        openapi_url=openapi_url,
        title=request.app.title + ' - ReDoc',
        redoc_js_url='/openapi-static/js/redoc.standalone.js',
        redoc_favicon_url='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMDAgMzAwIiB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCI+Cgk8ZGVmcz4KCQk8aW1hZ2Ugd2lkdGg9IjI5MiIgaGVpZ2h0PSIyOTIiIGlkPSJpbWcxIiBocmVmPSJkYXRhOmltYWdlL3BuZztiYXNlNjQsaVZCT1J3MEtHZ29BQUFBTlNVaEVVZ0FBQVNRQUFBRWtBUU1BQUFDOE45NnZBQUFBQVhOU1IwSUIyY2tzZndBQUFBWlFURlJGQUFBQUFBQUFwV2U1endBQUFBSjBVazVUQVA5YmtTSzFBQUFFT2tsRVFWUjRuTzJaUWJLak1BeEVvVmg0eVJGOEZCL05ISTJqY0lRcy95TDFtY0VCZ2xwdHFpZmh6MlF4M2lYMXdLMjJBVmxxd3N6SDJCeEhyRkR6Y0tSU2pib2ZxVnlqekp4MTZ1dEFWYUY1MXFoSm9yNGthdGFvU2FLZVUrWVQ2bHVpbnNMU0diWGJIOCtvMjBiMVo5Uys0clg5VmNaVC9xcnN1TGEvUi9mQUJqRDIyMUtya3NOU0JodjEwYUliL2pFQ0ZWQkhnSnMvcnpVNmlQeFYyZkdQT01QVHNJd09naXhUWXBDUEtZODZXaFprbWVFWVpIRjJRQ3FnMnA1WVVXWXdhanU4K1NiTXFHMlpGVVVZWHVhc0tNS00yc2lzNkZCdHo2eG9jT0U2WnNWaWtJbXBaVllzT214TW1leUtSWWVOQ1crKzZiQXhSVWExR0ZOZ3RpNDZCcmk1dDNYUk1jTE52YTJManNuOFFXM3RVUzFLMk5SYUNpVnNhbTFNa1ZFdHh0UXo4eHVNeVVuWTFKNUwyTlNpQkVKRmpKeWEzMk5NbVpudnFNU29nSkdqMERJNnBDS2pXdlNuWnd2WllPU0JMWkZJWmZESENTMGpBZFZXS1BDSExuZVVxQjc5eVd5NW5UK1VDa2hoT0dWMFBzblNLTElwV3FUNkNqVUJSVFpGZzFTb1VEZWtCazlsb0xvSzlTVlFDU2dYOUI5UXptdVZtanpWaXhTc1NCWXBzbG1EU01HNkpVWjFuaUpiK2tVcU1xckYxVlVwOG5nNHlpMUdHU28xdmtTUlI4MVJic25LeUpkUzA0OVJibUhMU1ArQWNxK1R5NmoyRFNwK0FqWDhwejZjOHRESFVxODlIWi96bmtDS3ZlVTA2aWZmcTFkK0ZhNzlwcjFERGVhMzl0MitNbE80TW9QUmNpWXQvM29ybDNPSG1NbFRMaFZSODlYUlU3aHNXaDZ0NWVSYWZxK2RGYlJ6aDNhRzBjNUQydG1xZGs1RFNqbnphZWRIN1N5cW5XdTFNM0xsdk8wS0p4T2pyRDIxT29BcjZJeWV3cHFDVnAvUWFoMWEzYVJXZzBHS2JBa1hPSzBOdVpDa09wTldzM0k2VjdHdStDalUwbHgxYWhWclEzS1ZycFd5SWJuYTJpcldsV0U5NVNxbFVoMVRxNGxxOVZXdFZxdlZmUk16MWRXUWFUMDZnRml0dHEzVnlYbk5IV1hRK3IyVElmVUNlRjhCWmZBZVJRSVpQV3ZxTk5qdlNNeXVEbVJvZlJpdHAwUDdReTMycWFSZVU4QjIxejdoVVVaaVBiRFNrTHJEYjdjakVreFEybWtZNHVQU3lWN2tRcHpOQkd2YnJ6SzJhK0laZExmelZjYnVZVDZqSm9uYTNUbURudTVJc2k3b0l3OFNOVXJVVGFMdUV2WGNxVmtTbGlSaDhZemFiVDN0WE85THBPM0NiVTdZMFMzSTM3Q0dZUlArTVFBV2pmek5qUW1vRm5WMHhodHo3ZkdQUEpPM1NVQWQwUWRKM2t3ZENmSXhnOUhCZ2l6TFluU2t1ZkwyTlRvQ3NhTE1ZRjVGMWErQ1ZjdXNLS0VidGJuMnRUSnFZKzNMWjlRR1p0Z3lnMUZiL1NLN05HZDBWRVMxdVpJcFdMV3Awcm0yYW50bVdJdHFNUTNaZFJpMUxxWFpkQmkxTGowcUk3N1d1VTVTOWhncm5XdWhKKzF5U2kxRGZyTnpQWUNFSCs1Y2s1NjBjdEtKMHFuSkNWMkdpK21kempYcFNSTUtEK0hhaWRVZEZjdDRzU2RORjFMclhHczk2WmM3MTBwUFdxdUkxTnBwU0ltZGF6cGNiVWlnYXVtQXExa0pWUHNXNWFwM2Y1dktGMUxwSFFyMmVaU29TdllIejE5bFUweVdxaXozMlB3Q1ZJalYySi9jbDJVQUFBQUFTVVZPUks1Q1lJST0iLz4KCQk8aW1hZ2Ugd2lkdGg9IjExNCIgaGVpZ2h0PSI4MyIgaWQ9ImltZzIiIGhyZWY9ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBSElBQUFCVEFRTUFBQUI1NDhHdEFBQUFBWE5TUjBJQjJja3Nmd0FBQUFaUVRGUkZBRVRVQUFBQW9TSnBpQUFBQUFKMFVrNVRBUDlia1NLMUFBQUFpMGxFUVZSNG5PM1VNUTZBSUF3RjBCb0hSby9BVVR3YUhLMUg4UWlPREFZRUJ2azJqY1lZallQZDNnTDBVNkFoYmJWUUx0dWNpa2V3ejNaZ1ZneE0wNG5uaTliV2N3ZG01ZnpRYiszUE5FYjZpM1lURUlvaHdUb2hUaVNHTjVMWm9UMVJqK2JuTGZlWDUwTkhyVC9iSEY2TS9hTmxSRHJ5L1VCNk5XMDAwNzMvUWZxTi84R0NSZjlsV2xZYUMycE03Z0tsb0FBQUFBQkpSVTVFcmtKZ2dnPT0iLz4KCTwvZGVmcz4KCTxzdHlsZT4KCQl0c3BhbiB7IHdoaXRlLXNwYWNlOnByZSB9Cgk8L3N0eWxlPgoJPHVzZSBpZD0iTGF5ZXIiIGhyZWY9IiNpbWcxIiB4PSI0IiB5PSI0IiAvPgoJPHVzZSBpZD0iTGF5ZXIiIGhyZWY9IiNpbWcyIiB4PSIxNDQiIHk9Ijc0IiAvPgo8L3N2Zz4='
    )


def _setup_openapi_and_ui_route(app: FastAPI) -> None:
    """
    设置OpenAPI和相关UI的路由

    :param app:FastAPI实例
    :return:None
    """
    # 设置静态文件路径
    openapi_static = Path(__file__).absolute().parent / 'openapi'
    if openapi_static.exists():
        app.mount('/openapi-static', StaticFiles(directory=openapi_static), name='openapi_static')
    # 添加自定义的OpenAPI
    if app.openapi_url:
        app.add_route(path=app.openapi_url, route=_custom_openapi, include_in_schema=False)
        base_url = app.openapi_url.removesuffix('.json')
        # 添加自定义的SwaggerUI
        if app.docs_url:
            docs_url = base_url + app.docs_url
            app.add_route(path=docs_url, route=_swagger_ui_html, include_in_schema=False)
            if app.swagger_ui_oauth2_redirect_url:
                oauth2_redirect_url = base_url + app.swagger_ui_oauth2_redirect_url
                app.add_route(path=oauth2_redirect_url, route=lambda _: get_swagger_ui_oauth2_redirect_html(),
                              include_in_schema=False)
        # 添加自定义的RedocUI
        if app.redoc_url:
            redoc_url = base_url + app.redoc_url
            app.add_route(path=redoc_url, route=_redoc_html, include_in_schema=False)


# noinspection PyTypeChecker
def enhance(
        app: FastAPI,
        *,
        cors: bool = True,
        cors_allow_credentials: bool = False,
        cors_allow_origins: Optional[List[str]] = None,
        cors_allow_methods: Optional[List[str]] = None,
        cors_allow_headers: Optional[List[str]] = None
) -> FastAPI:
    """
    增强FastAPI应用

    :param app:FastAPI实例对象
    :param cors: 是否启用CORS中间件
    :param cors_allow_credentials: 是否允许携带凭证
    :param cors_allow_origins: 允许的源列表
    :param cors_allow_methods: 允许的HTTP方法列表
    :param cors_allow_headers: 允许的HTTP头列表
    :return: 增强后的FastAPI实例
    """
    # 移除所有默认Route
    app.router.routes = []
    # 启用 CORS 中间件
    if cors:
        app.add_middleware(
            CORSMiddleware,
            allow_credentials=cors_allow_credentials,
            allow_origins=cors_allow_origins or ['*'],
            allow_methods=cors_allow_methods or ['*'],
            allow_headers=cors_allow_headers or ['*']
        )
    _setup_openapi_and_ui_route(app)
    return app


FastAPI.enhance = enhance
