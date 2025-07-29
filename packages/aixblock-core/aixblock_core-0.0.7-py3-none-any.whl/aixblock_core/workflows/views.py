import json
import logging
import time
import jwt
import requests
from compute_marketplace.models import Portfolio
from core.settings.base import BASE_BACKEND_URL, WORKFLOW_ENDPOINT
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from rest_framework.authtoken.models import Token
from users.models import Transaction
from workflows.function import get_external_project_id, get_key, create_key


api_key = None
signing_key = None
signing_key_id = None


def workflows_token(request):
    global signing_key, signing_key_id

    if not signing_key or not signing_key_id:
        key = get_key()

        if key is None:
            raise Exception("No workflow signing key found")

        signing_key = key["privateKey"]
        signing_key_id = key["id"]

    current_time = int(time.time())
    token = Token.objects.filter(user=request.user.id).first()

    payload = {
        "version": "v3",
        "externalUserId": request.user.email,
        "externalProjectId": get_external_project_id(request.user),
        "firstName": request.user.first_name,
        "lastName": request.user.last_name,
        "exp": current_time + (30 * 86400),  # Expire in 30 days
        "token": token.key if token else "",
        "url": BASE_BACKEND_URL,
    }

    token = jwt.encode(
        payload,
        signing_key,
        algorithm="RS256",
        headers={"kid": signing_key_id},
    )

    return HttpResponse(token)


def get_api_key():
    global api_key

    if api_key:
        return api_key

    key = get_key()

    if key is None:
        raise Exception("No workflow signing key found")

    api_key = key["apiKey"]
    return api_key


def workflows_listing(request):
    page = request.GET.get("page", "1")
    category = request.GET.get("category", "")
    name = request.GET.get("name", "")

    response = requests.get(
        f"{WORKFLOW_ENDPOINT}/api/v1/marketplace?page={page}&category={category}&name={name}",
        headers={
            'Authorization': f'Bearer {get_api_key()}',
        },
    )

    return HttpResponse(response.content, status=response.status_code, content_type="application/json")


def workflows_listing_detail(request, template_id):
    response = requests.get(f"{WORKFLOW_ENDPOINT}/api/v1/marketplace/{template_id}", headers={'Authorization': f'Bearer {get_api_key()}'})
    return HttpResponse(response.content, status=response.status_code, content_type="application/json")


@login_required
def workflows_create_template(request, template_id):
    try:
        template_res = requests.get(
            f"{WORKFLOW_ENDPOINT}/api/v1/marketplace/{template_id}",
            headers={'Authorization': f'Bearer {get_api_key()}'},
        )

        template = template_res.json()

        with transaction.atomic():
            if template["price"] > 0:
                buyer_portfolio = Portfolio.objects.select_for_update().filter(account_id=request.user.id).filter(token_symbol="USD").first()

                if buyer_portfolio.amount_holding < template["price"]:
                    return HttpResponseBadRequest(content=json.dumps({"detail": "You don't have enough balance"}), content_type='application/json')

                Transaction.objects.create(
                    user_id=request.user.id,
                    amount=-template["price"],
                    unit=Transaction.Unit.USD,
                    network=Transaction.Network.FIAT,
                    type=Transaction.Type.BUY_WORKFLOW_TEMPLATE,
                    description="Template #" + template["id"]
                )

                buyer_portfolio.amount_holding -= template["price"]
                buyer_portfolio.save()

                seller_portfolio = Portfolio.objects.select_for_update().filter(account_id=template["userId"]).filter(token_symbol="USD").first()

                if seller_portfolio:
                    seller_portfolio.amount_holding += template["price"]
                    seller_portfolio.save()
                else:
                    Portfolio.objects.create(
                        account=template["userId"],
                        token_symbol="USD",
                        token_name="United States Dollar",
                        amount_holding=template["price"],
                    )

                Transaction.objects.create(
                    user_id=template["userId"],
                    amount=template["price"],
                    description="Template #" + template["id"],
                    unit=Transaction.Unit.USD,
                    network=Transaction.Network.FIAT,
                    type=Transaction.Type.SELL_WORKFLOW_TEMPLATE,
                )

            response = requests.post(
                f"{WORKFLOW_ENDPOINT}/api/v1/marketplace/{template_id}/create-template",
                headers={'Authorization': f'Bearer {get_api_key()}'},
                json={"externalProjectId": get_external_project_id(request.user)},
            )

            return HttpResponse(response.content, status=response.status_code, content_type="application/json")
    except Exception as e:
        logging.error(e)
        return HttpResponseBadRequest(content=json.dumps({"detail": e.__str__()}), content_type='application/json')


def workflows_categories(request):
    response = requests.get(f"{WORKFLOW_ENDPOINT}/api/v1/marketplace/categories", headers={'Authorization': f'Bearer {get_api_key()}'})
    return HttpResponse(response.content, status=response.status_code, content_type="application/json")
