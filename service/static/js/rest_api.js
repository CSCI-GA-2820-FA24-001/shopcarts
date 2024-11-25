$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#shopcart_name").val(res.name);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_id").val("");
        $("#shopcart_name").val("");
        $("#item_shopcart_id").val("");
        $("#item_id").val("");
        $("#item_description").val("");
        $("#item_quantity").val("");
        $("#item_price").val("");
    }

    // Updates the flash message area with styles for success or failure
    function flash_message(message, isSuccess = true) {
        $("#flash_message").empty(); 
        $("#flash_message").removeClass("alert-success alert-danger"); 

        
        if (isSuccess) {
            $("#flash_message").addClass("alert alert-success");
        } else {
            $("#flash_message").addClass("alert alert-danger");
        }

        $("#flash_message").append(message); 
    }


    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-shopcart-btn").click(function () {
        $("#shopcart_id").val("");
        let name = $("#shopcart_name").val();

        let data = {
            "name": name,
            "items": []
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Shopcart created successfully!");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message,false);
        });
    });

    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-shopcart-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();
        let name = $("#shopcart_name").val();

        let data = {
            "name": name,
            "items":[]  // supplying an empty list of items does not delete any existing items
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Shopcart updated successfully!");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message,false);
        });
    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-shopcart-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Shopcart retrieved successfully!");
        });

        ajax.fail(function(res){
            clear_form_data();
            flash_message(res.responseJSON.message,false);
        });
    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-shopcart-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        });

        ajax.done(function(res){
            clear_form_data();
            flash_message("Shopcart has been deleted!");
        });

        ajax.fail(function(res){
            flash_message("Server error!",false);
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-shopcart-btn").click(function () {
        $("#flash_message").empty();
        clear_form_data();
    });

    // ****************************************
    // Search Shopcarts
    // ****************************************
    
    $("#search-shopcart-btn").click(function () {
        const shopcartID = $("#shopcart_id").val();
        const shopcartName = $("#shopcart_name").val();
      
        $("#flash_message").empty();
      
        let ajax = $.ajax({
          type: "GET",
          url: `/shopcarts`,
          contentType: "application/json",
          data: '',
        });
      
        ajax.done(function (res) {
          $("#shopcart_search_results tbody").empty();
      
          // Filter results using JavaScript
          const filteredShopcarts = res.filter((shopcart) => {
            let matchesID = shopcartID ? shopcart.id.toString() === shopcartID : true;
            let matchesName = shopcartName ? shopcart.name.includes(shopcartName) : true;
            return matchesID && matchesName;
          });
      
          // Build table rows
          let tableRows = "";
          filteredShopcarts.forEach((shopcart) => {
            tableRows += `<tr>
                            <td>${shopcart.id}</td>
                            <td>${shopcart.name}</td>
                          </tr>`;
          });
      
          // Append rows to table
          $("#shopcart_search_results tbody").append(tableRows);
      
          if (filteredShopcarts.length > 0) {
            flash_message("Shopcarts loaded successfully!");
          } else {
            flash_message("No shopcarts match the search criteria.",false);
          }
        });
      
        ajax.fail(function (res) {
          flash_message(res.responseJSON.message,false);
        });
    });

    // ****************************************
// Search Items
// ****************************************

$("#search-item-btn").click(function () {
    const shopcartID = $("#item_shopcart_id").val(); // Get Shopcart ID
    const itemID = $("#item_id").val(); // Get Item ID

    // Clear previous flash messages
    $("#flash_message").empty();

    // Validate the required field
    if (!shopcartID) {
        flash_message("Shopcart ID is required to search for items.",false);
        return; // Stop execution if Shopcart ID is missing
    }

    // Build the query string
    let queryString = `shopcart_id=${shopcartID}`;
    if (itemID) queryString += `&item_id=${itemID}`;

    // Make the AJAX call
    let ajax = $.ajax({
        type: "GET",
        url: `/items?${queryString}`,
        contentType: "application/json",
        data: ''
    });

    ajax.done(function (res) {
        // Clear previous search results
        $("#item_search_results tbody").empty();

        // Build table rows for search results
        let tableRows = "";
        res.forEach((item) => {
            tableRows += `<tr>
                            <td>${item.item_id}</td>
                            <td>${item.description}</td>
                            <td>${item.quantity}</td>
                            <td>${item.price}</td>
                          </tr>`;
        });

        // Append rows to the table
        $("#item_search_results tbody").append(tableRows);

        // Flash success message
        flash_message("Items loaded successfully!");
    });

    ajax.fail(function (res) {
        // Flash error message on failure
        flash_message(res.responseJSON.message,false);
    });
});

});
