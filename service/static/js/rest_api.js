$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        
        $("#shopcart_id").val(res.id);
        $("#shopcart_name").val(res.name);

        // Handle items array - taking first item for now
        // if (res.items && res.items.length > 0) {
        //     let item = res.items[0];
        // }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_name").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {
        let shopcart_name = $("#shopcart_name").val();

        let data = {
            "name": shopcart_name,
            "items": []
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {
        let id = $("#shopcart_id").val();
        let name = $("#shopcart_name").val();

        let data = {
            "name": name,
            "items": []
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {
        let id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {
        let id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_form_data()
            flash_message("Deleted Shopcart!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
    

    // ****************************************
    // Cancel a Shopcart
    // ****************************************

    $("#cancel-btn").click(function () {
        let id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${id}/clear`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        $("#shopcart_name").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for Orders
    // ****************************************

    $("#search-btn").click(function () {
        let shopcart_name = $("#shopcart_name").val();

        let queryString = "";

        if (shopcart_name) {
            queryString += 'name=' + shopcart_name;
        }

        // if (product_name) {
        //     if (queryString.length > 0) {
        //         queryString += '&';
        //     }
        //     queryString += 'product_name=' + product_name;
        // }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts${queryString ? '?' + queryString : ''}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">ID</th>';
            table += '<th class="col-md-2">Shopcart Name</th>';
            table += '</tr></thead><tbody>';
            
            let first = "";
            for(let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                table += `<tr id="row_${i}">`;
                table += `<td>${shopcart.id}</td>`;
                table += `<td>${shopcart.name}</td>`;
                table += '</tr>';

                if (i == 0) {
                    first = shopcart;
                }

            }

            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (first != "") {
                update_form_data(first)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************************
    //  U T I L I T Y   F U N C T I O N S  F O R  I T E M S
    // ****************************************************

    // Updates the form with data from the response
    function update_item_form_data(res) {
            $("#item_id").val(res.id);
            $("#item_name").val(res.item_id);
            $("#item_description").val(res.description);
            $("#item_quantity").val(res.quantity);
            $("#item_price").val(res.price);
    }

    // clears the item form data
    function clear_item_form_data() {
        $("#shopcart_id_item").val("");
        $("#item_id").val("");
        $("#item_name").val("");
        $("#item_description").val("");
        $("#item_quantity").val("");
        $("#item_price").val("");
    }

    // Updates the flash message item area
    function flash_item_message(message) {
        $("#flash_message_item").empty();
        $("#flash_message_item").append(message);
    }

    // ****************************************
    // Create an item in Order
    // ****************************************

    $("#create-item-btn").click(function () {
        let shopcart_id = $("#shopcart_id_item").val();
        let item_name = $("#item_name").val();
        let description = $("#item_description").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        let data = {
            "shopcart_id": shopcart_id,
            "item_id": item_name,
            "description": description,
            "quantity": parseInt(quantity),
            "price": parseInt(price)
        };

        $("#flash_message_item").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/api/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_item_message("Success")
        });

        ajax.fail(function(res){
            flash_item_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-item-btn").click(function () {

        let shopcart_id = $("#shopcart_id_item").val();
        let item_id = $("#item_id").val();
        let item_name = $("#item_name").val();
        let description = $("#item_description").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        let data = {
            "shopcart_id": shopcart_id,
            "item_id": item_name,
            "description": description,
            "quantity": parseInt(quantity),
            "price": parseInt(price)
        };

        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_item_message("Success")
        });

        ajax.fail(function(res){
            flash_item_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve all items in Order
    // ****************************************

    $("#retrieve-item-btn").click(function () {
        let shopcart_id = $("#shopcart_id_item").val();
        let item_id = $("#item_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_item_form_data(res)
            flash_item_message("Success")
        });

        ajax.fail(function(res){
            clear_item_form_data();
            flash_item_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Delete an item in Order
    // ****************************************

    $("#delete-item-btn").click(function () {
        let shopcart_id = $("#shopcart_id_item").val();
        let item_id = $("#item_id").val();

        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_item_form_data()
            flash_item_message("Item has been Deleted!")
        });

        ajax.fail(function(res){
            flash_item_message("Server error!")
        });
    });
    

    // ****************************************
    // Clear the item form
    // ****************************************

    $("#clear-item-btn").click(function () {
        clear_item_form_data();
        clear_form_data();
    });

    // ****************************************
    // Search for items in an Order
    // ****************************************

    $("#search-item-btn").click(function () {
        let shopcart_id = $("#shopcart_id_item").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        let queryString = "";

        if (quantity) {
            queryString += 'quantity=' + quantity;
        }

        if (price) {
            if (queryString.length > 0) {
                queryString += '&';
            }
            queryString += 'price=' + price;
        }
        
        $("#flash_message_item").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}/items${queryString ? '?' + queryString : ''}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results_item").empty();
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">Item ID</th>';
            table += '<th class="col-md-2">Item Name</th>';
            table += '<th class="col-md-2">Description</th>';
            table += '<th class="col-md-2">Quantity</th>';
            table += '<th class="col-md-2">Price</th>';
            table += '</tr></thead><tbody>';
            
            let firstItem = "";
            flash_item_message("len="+res.length)
            for(let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr id="row_${i}">`;
                table += `<td>${item.id}</td>`;
                table += `<td>${item.item_id}</td>`;
                table += `<td>${item.description}</td>`;
                table += `<td>${item.quantity}</td>`;
                table += `<td>${item.price}</td>`;
                table += '</tr>';
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results_item").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_item_form_data(firstItem)
            }

            flash_item_message("Success")
        });

        ajax.fail(function(res){
            flash_item_message(res.responseJSON.message)
        });
    });

});