######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Pet Steps

Steps file for Pet.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following shopcarts")
def step_impl(context):
    """Delete all shopcarts and load new ones"""

    # Get a list all of the shopcarts
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for shopcart in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{shopcart['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new shopcarts
    for row in context.table:
        payload = {
            "name": row["name"],
            "items": [],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given("the following items")
def step_impl(context):
    """Load new items"""

    # Get a list all of the shopcarts
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete all shopcart items in the shopcarts one by one
    shopcart_ids = []
    for shopcart in context.resp.json():
        context.resp = requests.put(
            f"{rest_endpoint}/{shopcart['id']}/clear", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_200_OK)
        shopcart_ids.append(shopcart["id"])

    # load the database
    idx = 0
    cnt = 0

    for row in context.table:
        shopcart_id = shopcart_ids[idx]
        payload = {
            "shopcart_id": shopcart_id,
            "item_id": row["item_id"],
            "description": row["description"],
            "quantity": int(row["quantity"]),
            "price": int(row["price"]),
        }
        context.resp = requests.post(
            f"{rest_endpoint}/{shopcart_id}/items", json=payload, timeout=WAIT_TIMEOUT
        )

        cnt += 1
        if cnt == 3:
            idx += 1

        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
