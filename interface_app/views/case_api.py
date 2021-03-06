from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from interface_app.models import TestCase
from project_app.models import Project, Module
from test_platform.common import response_succeed, response_fail
import requests
import json


@login_required
def debug_case(request):
    if request.method == "POST":
        url = request.POST.get("url", "")
        method = request.POST.get("method", "").upper()
        param_type = request.POST.get("paramType", "").upper()
        headers = json.loads(request.POST.get("headers").replace("'", "\""))
        params = json.loads(request.POST.get("params").replace("'", "\""))

        if url == "" or method == "" or param_type == "":
            return response_fail("URL、请求方法、请求参数类型不能为空！")

        if method == "GET":
            if param_type == "FORM-DATA":
                r = requests.get(url, params=params, headers=headers)
            else:
                return response_fail("请求参数类型错误！")

        if method == "POST":
            if param_type == "FORM-DATA":
                r = requests.post(url, data=params, headers=headers)
            elif param_type == "JSON":
                r = requests.post(url, json=params, headers=headers)
            else:
                return response_fail("请求参数类型错误！")

        return response_succeed(data=r.text)
    else:
        return response_fail("该接口只支持POST请求！")


@login_required
def get_projects_and_modules(request):
    if request.method == "GET":
        projects = Project.objects.all()
        project_list = []
        for project in projects:
            current_project = {"projectName": project.name}
            modules = Module.objects.filter(project_id=project.id)
            if len(modules) != 0:
                module_names = []
                for module in modules:
                    module_names.append(module.name)
                current_project["moduleNames"] = module_names

            project_list.append(current_project)

        return response_succeed(data={"projects": project_list})
    else:
        return response_fail("该接口只支持GET请求！")


@login_required
def save_case(request):
    if request.method == "POST":
        module_name = request.POST.get("moduleName", "")
        name = request.POST.get("name", "")
        url = request.POST.get("url", "")
        method = request.POST.get("method", "").upper()
        param_type = request.POST.get("paramType", "")
        headers = request.POST.get("headers", "{}")
        params = request.POST.get("params", "{}")
        assert_text = request.POST.get("assertText", "")

        if module_name == "" or name == "" or url == "" or method == "" or param_type == "":
            return response_fail("模块名、用例名、url、请求方法、请求参数类型不能为空！")

        case = TestCase.objects.create(
            module=Module.objects.get(name=module_name),
            name=name,
            url=url,
            request_method=method,
            request_headers=headers,
            request_params_type=param_type,
            request_params=params,
            response_assert=assert_text,
        )

        if case is not None:
            return response_succeed("保存成功！")
        else:
            return response_fail("未知错误！保存失败！")

    else:
        return response_fail("该接口只支持POST请求！")


@login_required
def get_case_info(request, case_id):
    if case_id:
        target_case = TestCase.objects.get(id=case_id)
        response_data = {}
        response_data["name"] = target_case.name
        response_data["url"] = target_case.url
        response_data["method"] = target_case.request_method
        response_data["headers"] = target_case.request_headers
        response_data["paramsType"] = target_case.request_params_type
        response_data["params"] = target_case.request_params
        response_data["assertText"] = target_case.response_assert
        module = target_case.module
        response_data["moduleName"] = module.name
        response_data["projectName"] = module.project.name
        return response_succeed(data=response_data)
    else:
        return response_fail("用例ID不存在！")


@login_required
def update_case(request, case_id):
    if request.method == "POST":
        module_name = request.POST.get("moduleName", "")
        name = request.POST.get("name", "")
        url = request.POST.get("url", "")
        method = request.POST.get("method", "").upper()
        param_type = request.POST.get("paramType", "")
        headers = request.POST.get("headers", "{}")
        params = request.POST.get("params", "{}")
        assert_text = request.POST.get("assertText", "")

        if module_name == "" or name == "" or url == "" or method == "" or param_type == "":
            return response_fail("模块名、用例名、url、请求方法、请求参数类型不能为空！")

        case = TestCase.objects.filter(id=case_id).update(
            module=Module.objects.get(name=module_name),
            name=name,
            url=url,
            request_method=method,
            request_headers=headers,
            request_params_type=param_type,
            request_params=params,
            response_assert=assert_text,
        )

        if case == 1:
            return response_succeed("更新成功！")
        else:
            response_fail("更新失败！")
    else:
        return response_fail("该接口只支持POST请求！")


@login_required
def assert_result(request):
    if request.method == "POST":
        response_result = request.POST.get("response_result", "")
        assert_text = request.POST.get("assert_text", "")

        if response_result == "" or assert_text == "":
            return response_fail("验证数据或者响应结果不能为空！")

        try:
            assert assert_text in response_result
        except AssertionError:
            return response_fail("验证失败！")
        else:
            return response_succeed("验证成功！")
    else:
        return response_fail("该接口只支持POST请求！")
