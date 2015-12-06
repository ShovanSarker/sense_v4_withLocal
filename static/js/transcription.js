/**
 * Created by Tanvir on 12/7/2014.
 */

//Global elements
var decPoint = 2,
    editProductFlag = false,
    bodySelector = $('body'),
    tranCallList = $("#tranCallList"),
    transactionDetails = $("#transactionDetails"),
    registrationCallList = $("#registrationCallList"),
    failList = $("#failedTranslationList"),
    preTranslationList = $("#previousTransactions"),
    allProductsPrice = [],
    product_arr = [],
    subscriberList = [],
    subscriber_ids = [],
    mediaBaseURL = "http://app.hishab.co/media/",
    transactionDetailsBaseUrl = 'http://app.hishab.co/detailed_transaction/?id=',
    staticContentURL = "http://app.hishab.co/product_subscriber_list/",
    callListURL = "http://app.hishab.co/voice_record_list/",
    registrationListURL = "http://app.hishab.co/voice_record_list/",
    failListUrl = "http://app.hishab.co/failed_voice_record_list/",
    preTransListUrl = "http://app.hishab.co/completed_voice_record_list_transaction_id/",
    addProductURL = "http://app.hishab.co/add_product_outside/",
    addSubscriberURL = "http://app.hishab.co/addsubscriber_info_outside/",
    saveTransactionURL = "http://app.hishab.co/add_transaction/",
    failTransactionURL = "http://app.hishab.co/failed_transaction/",
    saveSubscriberURL = "http://app.hishab.co/addsubscriber_info_outside/",
    errorDiv = $(".modalError"),
    errorText = $(".alertText"),
    infoDiv = $(".modalInfo"),
    infoText = $(".infoText"),
    formSection_1 = false,
    formSection_2 = false,
    formSection_3 = false,
    reviewSection = $("#reviewProducts"),
    product_name = $('#product_name'),
    product_quantity = $('#product_quantity'),
    product_unit_price = $('#product_unit_price'),
    transTotalField = $('#transTotal'),
    transPaidField = $('#transPaid'),
    transDueField = $('#transDue'),
    transOtherParty = $('#transOtherParty'),
    transNoSub = $('#no_subscriber'),
    transDistributor = $('#is_distributor'),
    reviewTotal = $("#reviewTotal"),
    reviewPaid = $("#reviewPaid"),
    reviewDue = $("#reviewDue"),
    reviewOtherParty = $("#reviewOtherParty"),
    caller_id = $('#caller_id'),
    add_subscriber_intro_id = $('#add_subscriber_intro_id'),
    call_id = $('#call_id'),
    distributorTransaction = $('#distributorTransaction'),
    transactionProducts = $('#transactionProducts'),
    transactionTotalEstimated = $('#transactionTotalEstimated'),
    transactionTotal = $('#transactionTotal'),
    transactionPaid = $('#transactionPaid'),
    transactionDue = $('#transactionDue'),
    transactionOtherParty = $('#otherParty'),
    timetaken = $('#timetaken');


//TODO optimozation, use dropdown on product it will allow us to check only against product_id and send the product ID in product staring
//TODO Form Reset individual form and final form, also the values


// Custom scripts
$(document).ready(function () {

    /************
     * Global
     ************/

    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green'
    });

    var startTime = 0,
        endTime = 0,
        totalTime = 0;

    /********************
     * Static Contents
     *******************/

    //Generate the list on page load
    getTransList();

    //Collect the static data
    $.getJSON(staticContentURL, function (data) {
        $.each(data.products, function (key, val) {
            allProductsPrice.push(val.name + ' -- (' + val.avg_price + ')');
            //productList.push(val.name);

        });

        $.each(data.subscribers, function (key, val) {
            subscriberList.push(val.name + ' -- (' + val.number + ')');
            subscriber_ids.push(val.id);

        });

    });

    /*************************
     * Page Menu and buttons
     *************************/


    //Refresh Button action
    $("#refreshCallList").on('click', function () {
        //Remove the list to avoid duplication
        $('.call-list').remove();
        //regenerate the list
        getTransList();
    });
    $("#refreshRegList").on('click', function () {
        //Remove the list to avoid duplication
        $('.registration-list').remove();
        //regenerate the list
        getRegistrationList();
    });
    $("#refreshFaillList").on('click', function () {
        //Remove the list to avoid duplication
        $('.fail-list').remove();
        //regenerate the list
        getFailList();
    });
    $("#refreshPreTransList").on('click', function () {
        //Remove the list to avoid duplication
        $('.pre-trans-list').remove();
        //regenerate the list
        getPreTransList();
    });

    //Transaction link button action
    $("#transList").on('click', function () {
        //Remove the list to avoid duplication
        $('.call-list').remove();

        //if the list is hidden then show it first
        if (tranCallList.hasClass("hide")) {
            transactionDetails.addClass("hide");
            tranCallList.removeClass('hide');
            failList.addClass("hide");
            preTranslationList.addClass("hide");
            registrationCallList.addClass("hide");
        }
        //regenerate the list
        getTransList();
    });

    //registration link button action
    $("#regList").on('click', function () {

        //Remove the list to avoid duplication
        $('.registration-list').remove();
        $('.call-list').remove();


        //if the list is hidden then show it first
        if (registrationCallList.hasClass("hide")) {
            tranCallList.addClass("hide");
            transactionDetails.addClass("hide");
            failList.addClass("hide");
            preTranslationList.addClass("hide");
            registrationCallList.removeClass('hide');
        }

        //regenerate the list
        getRegistrationList();
    });

    //fail link button action
    $("#failList").on('click', function () {
        //Remove the list to avoid duplication
        $('.fail-list').remove();

        //if the list is hidden then show it first
        if (failList.hasClass("hide")) {
            tranCallList.addClass("hide");
            transactionDetails.addClass("hide");
            registrationCallList.addClass('hide');
            preTranslationList.addClass('hide');
            failList.removeClass("hide")
        }
        //regenerate the list
        getFailList();
    });

    //All transaction list
    $("#preTranslationList").on('click', function () {
        //Remove the list to avoid duplication
        $('.pre-trans-list').remove();

        //if the list is hidden then show it first
        if (preTranslationList.hasClass("hide")) {
            tranCallList.addClass("hide");
            registrationCallList.addClass('hide');
            transactionDetails.addClass("hide");
            failList.addClass("hide");
            preTranslationList.removeClass('hide');
        }
        //regenerate the list
        getPreTransList();
    });

    //back button from transaction details
    $("#transDetailsBack").on('click', function () {
        $('.call-list').remove();
        transactionDetails.addClass("hide");
        tranCallList.removeClass('hide');
        registrationCallList.addClass("hide");
        failList.addClass("hide");
        //regenerate the list
        getTransList();
    });


    /**********************************
     * Translate button and others
     **********************************/

    //Open transaction details page
    bodySelector.on("click", ".transButton", function () {

        $("#newProduct")[0].reset();
        $("#newSubscriber")[0].reset();
        $("#productForm")[0].reset();
        $("#transPaymentInfo")[0].reset();
        $("#finalForm")[0].reset();

        tranCallList.addClass("hide");
        transactionDetails.removeClass("hide");

        //Build the details header
        var $this = $(this),
            callerLevel = $this.data("caller_level").toString(),
            badge = levelBadge(callerLevel),
            audioStrings = $this.data('audiofiles').split(","),
            current_caller_id = $this.data('caller_id'),
            current_caller = $this.data('caller'),
            headerString = current_caller + '&nbsp;[' + $this.data("caller_number") + ']&nbsp;<span class="badge badge-' + badge.levelClass + '">' + badge.levelText + '</span>';

        //Set the page heading
        $('#transDetailsHeader').html(headerString);
        $('#failCallerName').html($this.data("caller")+' ('+$this.data("caller_number")+')');
        $('#failCallerID').val($this.data('call_id'));


        //Caller and call info to final form
        startTime = new Date().getTime();
        call_id.val($this.data('call_id'));
        caller_id.val(current_caller_id);
        add_subscriber_intro_id.val(current_caller_id);
        $('#add_subscriber_intro_name').val(current_caller);

        //Add the Audio
        $.each(audioStrings, function (key, val) {
            var fileString =  mediaBaseURL+val,
                audioLiNumber = parseInt(key)+ 1,
                audioLi = "#transAudio_"+ audioLiNumber,
                player_id = audioLi+"_player";

            $(player_id).attr('src', fileString);
            $(audioLi).removeClass('hide');
        });
    });

    //listen the audio button for failedTranslationList
    bodySelector.on("click", ".listenButton", function () {

        var audioStrings = $(this).data('audiofiles').split(",");

        //Add the Audio
        $.each(audioStrings, function (key, val) {
            var fileString =  mediaBaseURL+val,
                audioLiNumber = parseInt(key)+ 1,
                audioLi = "#failAudio_"+ audioLiNumber,
                player_id = audioLi+"_player";

            $(player_id).attr('src', fileString);
            $(audioLi).removeClass('hide');
        });

        //$('#failAudio_player').attr('src', $(this).data('audiofiles'));
        $('#listenFailedAudioModal').modal('show');
    });

    //New registration button
    bodySelector.on("click", ".newRegistrationButton", function () {

        $("#newSubscriber")[0].reset();

        var buttonSelector = $(this),
            phoneSelector = $('#phone');
        if(buttonSelector.data('reg_request') == '1'){

            var audioStrings = $(this).data('audiofiles').split(",");

            //Add the Audio
            $.each(audioStrings, function (key, val) {
                var fileString =  mediaBaseURL+val,
                    audioLiNumber = parseInt(key)+ 1,
                    player_id = "#regAudio_player_"+ audioLiNumber;

                $(player_id).attr('src', fileString).removeClass('hide');
            });

            $('#regAudioSection').removeClass('hide');

            phoneSelector.val(buttonSelector.data('caller_number'));
            phoneSelector.parent().addClass('hide');

            $('#is_reg').val('1');
            $('#record_id').val(buttonSelector.data('call_id'));

        } else {
            $('#is_reg').val('0');
            phoneSelector.parent().removeClass('hide')
        }

        $('#addSubscriberModal').modal('show');
    });


    /**********************************
     * Transaction entry page functions
     **********************************/

    //Functions for quick search on product list

    var substringMatcher = function (strs) {
        return function findMatches(q, cb) {
            var matches, substrRegex;

            // an array that will be populated with substring matches
            matches = [];

            // regex used to determine if a string contains the substring `q`
            substrRegex = new RegExp(q, 'i');

            // iterate through the pool of strings and for any string that
            // contains the substring `q`, add it to the `matches` array
            $.each(strs, function (i, str) {
                if (substrRegex.test(str)) {
                    // the typeahead jQuery plugin expects suggestions to a
                    // JavaScript object, refer to typeahead docs for more info
                    matches.push({value: str});
                }
            });

            cb(matches);
        };
    };

    $('#product_name_box').find('.typeahead').typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: 'product_name',
            displayKey: 'value',
            source: substringMatcher(allProductsPrice)
        });

    $('#other_party_box').find('.typeahead').typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: 'transOtherParty',
            displayKey: 'value',
            source: substringMatcher(subscriberList)
        });


    /**
     * Add new product submission
     * --- Send the data via AJAX and on successful add push the product name and avg price to the product array
     * --- then close the modal
     */
    $("#newProduct").submit(function (event) {

        // Stop form from submitting normally
        event.preventDefault();

        // Get some values from elements on the page:
        var $form = $(this),
            product_name = $form.find("input[name='name']").val(),
            product_price = $form.find("input[name='retail_price']").val();
        //TODO: set form action

        // Send the data using post
        var posting = $.post(addProductURL, $form.serialize());

        // Put the results in a div
        posting.done(function (data) {
            $('#addProductModal').modal('toggle');
            var st = data;
            if(st == "ok"){
                $(".alert").alert();
                infoText.html('Add product successful');
                infoDiv.removeClass('hide');
                allProductsPrice.push(product_name + ' -- (' + product_price + ')');
                $($form)[0].reset();
            } else {
                $(".alert").alert();
                errorText.html('Add product failed. ['+st+']');
                errorDiv.removeClass('hide');
            }
        });

        posting.fail(function () {
            errorText.html("Add product failed, please try again");
            errorDiv.removeClass('hide');
        })
    });

    /**
     * New subscriber submit function
     */
    $("#newSubscriber").submit(function (event) {

        // Stop form from submitting normally
        event.preventDefault();

        // Get some values from elements on the page:
        var $form = $(this),
            subscriber_name = $form.find("input[name='name']").val(),
            subscriber_phone = $form.find("input[name='phone']").val(),
            is_reg = $form.find("input[name='is_reg']").val(),
            subscriber_intro_name = $form.find("input[name='add_subscriber_intro_name']").val();

        // Send the data using post
        var posting = $.post(addSubscriberURL, $form.serialize());

        // Put the results in a div
        posting.done(function (data) {
            if(data != 'error'){
                if(parseInt(is_reg) == 1){
                    subscriberList.push(subscriber_name + ' -- (' + subscriber_phone + ')');
                } else {
                    subscriberList.push(subscriber_name + ' -- (' + subscriber_intro_name + ')');
                }
                subscriber_ids.push(parseInt(data));
            } else {
                errorText.html("Add subscriber failed, please try again");
                errorDiv.removeClass('hide');
            }
        });

        posting.fail(function () {
            errorText.html("Add subscriber failed, please try again");
            errorDiv.removeClass('hide');
        });
        $('#addSubscriberModal').modal('hide');
    });


    /**
     * Add Product to review table
     */
    $("#productForm").submit(function (event) {

        event.preventDefault();

        var $form = $(this),
            product_name_price = $form.find("input[name='product_name']").val(),
            p_quantity = $form.find("input[name='product_quantity']").val(),
            p_unit_price = $form.find("input[name='product_unit_price']").val(),
            productName = product_name_price.split(" -- "),
            p_name = productName[0];

        //Check if the product in the list
        if ($.inArray(product_name_price, allProductsPrice) == -1) {
            product_name.parent().addClass("has-error");
            errorText.html("No such product, You can add the product by clicking on Add Product Button");
            errorDiv.removeClass('hide');

        } else if (!(p_quantity != "" && p_quantity != 0)) {
            product_quantity.parent().addClass("has-error");
            errorText.html("Product quantity cannot be empty");
            errorDiv.removeClass('hide');

        } else if (!(p_unit_price != "" && p_unit_price != 0)) {
            p_unit_price.parent().addClass("has-error");
            errorText.html("Product unit price cannot be empty");
            errorDiv.removeClass('hide');

        } else {

            formSection_1 = true;


            //Check if the product is already added

            //check if there is value in product array if not add the first value without checking
            if (typeof product_arr !== 'undefined' && product_arr.length > 0) {
                var match_found = 0,
                    product_string = "",
                    new_quantity = 0,
                    matched_position = 0;

                //for each element of the array check for match
                for (var i = 0; i < product_arr.length; i++) {
                    var exProductString = product_arr[i].split("--"),
                        exProduct = exProductString[0];

                    //TODO we are detecting the duplicate value but the what if the different entry has different unit price
                    if (exProduct == p_name) {
                        match_found = 1;
                        matched_position = parseInt(i);
                        new_quantity = exProductString[1];
                    }
                }
                if (match_found == 1) {
                    //product_arr.splice(matched_position, 1);
                    if (editProductFlag) {
                        p_quantity = parseFloat(p_quantity).toFixed(decPoint);
                        editProductFlag = false;
                    } else {
                        p_quantity = (parseFloat(p_quantity) + parseFloat(new_quantity)).toFixed(decPoint);
                    }
                    //p_quantity = (parseFloat(p_quantity) + parseFloat(new_quantity)).toFixed(decPoint);
                    product_string = p_name + "--" + p_quantity + "--" + p_unit_price;
                    product_arr[matched_position] = product_string;
                } else {
                    product_string = p_name + "--" + p_quantity + "--" + p_unit_price;
                    product_arr.push(product_string);
                }
            } else {
                product_arr.push(p_name + "--" + p_quantity + "--" + p_unit_price);
            }


            //Re-int the product entry to update the new entry
            //TODO optimize the double string operation

            productString = "";
            reviewSection.find("tbody").empty();
            var totalPrice = 0;

            for (var p = 0; p < product_arr.length; p++) {

                var printProductString = product_arr[p].split("--"),
                    ppName = printProductString[0],
                    ppQuantity = printProductString[1],
                    ppUnitPrice = printProductString[2];

                productString = productString + ";" + ppName + "-" + ppQuantity + "-" + ppUnitPrice;
                var rowString = "<tr>" +
                    "<td>" + ppName + "</td>" +
                    "<td>" + ppQuantity + "</td>" +
                    "<td>" + ppUnitPrice + "</td>" +
                    "</tr>";

                totalPrice = (parseFloat(totalPrice) + (parseFloat(ppUnitPrice) * parseFloat(ppQuantity))).toFixed(decPoint);
                reviewTotal.html(totalPrice);

                reviewSection.find("tbody").append(rowString);
            }

            transTotalField.val(totalPrice);
            transactionTotalEstimated.val(totalPrice);
            transactionProducts.val(productString);

            //Clear the fields
            product_name.val("");
            product_quantity.val("");
            product_unit_price.val("");

            //Clear error (if any)
            clearError();

        }

        return false;
    });


    /**
     * Bind review product edit button
     */
    bodySelector.on('click', '.editProductButton', function () {
        product_name.val($(this).data('product_name'));
        product_quantity.val($(this).data('product_q'));
        product_unit_price.val($(this).data('product_p'));
        editProductFlag = true;
    });

    /**
     * Bind review product delete button
     * TODO Remove the product from array, adjust the totals
     */
    bodySelector.on('click', '.deleteProductButton', function () {
        console.log('not done');
    });

    /**
     * When the paid field change
     */
    transPaidField.on('input', function () {
        var newDue = (parseFloat(transTotalField.val()) - parseFloat(transPaidField.val())).toFixed(decPoint);
        transDueField.val(newDue);
    });

    /**
     * When the due field change
     */
    transDueField.on('input', function () {
        var newPaid = (parseFloat(transTotalField.val()) - parseFloat(transDueField.val())).toFixed(decPoint);
        transPaidField.val(newPaid);
    });

    /**
     * Add payment info to review table
     */
    $("#transPaymentInfo").submit(function (event) {

        event.preventDefault();

        var p_bill = transTotalField.val(),
            p_paid = transPaidField.val(),
            p_due = transDueField.val();

        if (p_bill != "" && p_bill != 0) {

            reviewTotal.html(p_bill);
            transactionTotal.val(p_bill);

            if (p_due != "" && p_paid != "") {

                formSection_2 = true;

                reviewDue.html(p_due);
                transactionDue.val(p_due);

                reviewPaid.html(p_paid);
                transactionPaid.val(p_paid);

                //Clear error (if any)
                $(".alert").alert();
                transTotalField.parent().removeClass("has-error");
                transDueField.parent().removeClass("has-error");
                transPaidField.parent().removeClass("has-error");

            } else {
                transPaidField.parent().addClass("has-error");
                transDueField.parent().addClass("has-error");
                errorText.html("Paid & due both fields can not be empty");
                errorDiv.removeClass('hide');
            }
        } else {
            transTotalField.parent().addClass("has-error");
            errorText.html("Total bill field is empty");
            errorDiv.removeClass('hide');

        }
        return false;
    });

    /**
     * Add second party info to review table
     */
    $("#trans2ndParty").submit(function (event) {
        event.preventDefault();

        var the_party = transOtherParty.val();

        if (the_party != "" || transNoSub.prop('checked')) {

            formSection_3 = true;

            //find the other party ID
            var sub_id = 0;
            if (!transNoSub.prop('checked')) {

                var sub_position = $.inArray(the_party, subscriberList);
                sub_id = subscriber_ids[sub_position];
            }

            if (transDistributor.prop('checked')) {
                distributorTransaction.val(1);
            } else {
                distributorTransaction.val(0);
            }

            transactionOtherParty.val(sub_id);
            reviewOtherParty.html(the_party);

            $(".alert").alert();
            transOtherParty.parent().removeClass("has-error");

        } else {
            transOtherParty.parent().addClass("has-error");
            errorText.html("2nd Party information fields can not be empty");
            errorDiv.removeClass('hide');
        }

        return false;
    });

    /**
     * Build and send all details to server
     */
    $("#finalForm").submit(function (event) {

        event.preventDefault();
        if (formSection_1 && formSection_2 && formSection_3) {

            endTime = new Date().getTime();
            totalTime = (endTime - startTime) / 1000;

            timetaken.val(totalTime);


            // Send the data using post
            var posting = $.post(saveTransactionURL, $(this).serialize());

            // Put the results in a div
            posting.done(function (data) {
                //if(data.status == 'ok'){
                $(".alert").alert();
                location.reload(true);
                //} else {
                //    errorText.html("Something went wrong, please refresh the page and try again.");
                //    errorDiv.removeClass('hide');
                //}
            });

            posting.fail(function () {
                errorText.html("Something went wrong, please refresh the page and try again.");
                errorDiv.removeClass('hide');
            });

        } else {
            errorText.html("All fields must be filled");
            errorDiv.removeClass('hide');
        }
        return false;
    });


    /**
     * Build and send the Registration details
     */
    $("#finalForm_reg").submit(function (event) {
        event.preventDefault();
        // Send the data using post
        var posting = $.post(saveSubscriberURL, $(this).serialize());
        // Put the results in a div
        posting.done(function (data) {
            if(data.status == 'ok'){
            $(".alert").alert();
            location.reload(true);
            }
            //else {
            //    errorText.html("Something went wrong, please refresh the page and try again.");
            //    errorDiv.removeClass('hide');
            //}
        });
    });


    /**
     * Mark the trasaction as fail
     */
    $("#translationFailedForm").submit(function (event) {
        event.preventDefault();
        //TODO add validation

        var posting = $.post(failTransactionURL, $(this).serialize());

        posting.done(function (data) {
            if(data.status == 'ok'){
                $(".alert").alert();
                location.reload(true);
            } else {
                errorText.html("Something went wrong, please refresh the page and try again.");
                errorDiv.removeClass('hide');
            }
        });

        posting.fail(function () {
            errorText.html("Something went wrong, please refresh the page and try again.");
            errorDiv.removeClass('hide');
        });
    });


    /**************************************
     * Transaction Details page functions
     *************************************/

    bodySelector.on('click', '.preTranDetails', function () {

        var url = transactionDetailsBaseUrl+$(this).data('transaction_id');
        $.getJSON(url, function (data) {
            $('#tdTid').html(data.transaction_id);
            $('#tdDate').html(data.date);
            $('#tdSubscriber').html(data.seller);
            $('#tdConsumer').html(data.consumer);
            $('#tdTranslator').html(data.translate_by);
            $('#tdTotal').html(data.total);
            $('#tdPaid').html(data.paid);
            $('#tdDue').html(data.due);

            var counter = 1,
                items = [];
        $.each(data.products, function (key, val) {
            row = '<tr>' +
                    '<td class="text-center">' + counter + '</td>' +
                    '<td class="text-center"><strong>' + val.name + '</strong></td>' +
                    '<td class="text-center">' + val.quantity +'&nbsp;'+val.unit+ '</td>' +
                    '<td class="text-center">' + val.unit_price + '</td>' +
                    '<td class="text-center">' + (parseFloat(val.quantity).toFixed(2)*parseFloat(val.unit_price).toFixed(2)) + '</td>' +
                    '</tr>';
            items.push(row);
            counter ++;
        });
        //Build the HTML
        $("<tbody/>", {
            "class": "pre-trans-list",
            html: items.join("")
        }).appendTo("#transactionProductTable");
        });
        $('#transactionInfo').modal('show');
    });
});


function clearError() {
    //TODO need to enhance this function to reuse more
    $(".alert").alert();
    product_name.parent().removeClass("has-error");
    product_quantity.parent().removeClass("has-error");
}

//Generate badge for different user level
function levelBadge(level) {

    var badge = [];
    switch (level) {
        case "beginner":
            //badge = {firstName:"John", lastName:"Doe", age:46};
            badge.levelClass = "primary";
            badge.levelText = "Beginner";
            break;
        case "intermediate":
            badge.levelClass = "success";
            badge.levelText = "Intermediate";
            break;
        case "advance":
            badge.levelClass = "danger";
            badge.levelText = "Advance";
            break;
        case "1":
            //badge = {firstName:"John", lastName:"Doe", age:46};
            badge.levelClass = "primary";
            badge.levelText = "Beginner";
            break;
        case "2":
            badge.levelClass = "success";
            badge.levelText = "Intermediate";
            break;
        case "3":
            badge.levelClass = "danger";
            badge.levelText = "Advance";
            break;
        default:
            badge.levelClass = "Plain";
            badge.levelText = "Unknown";
    }
    return badge;
}

//Generate Pending Translation List
function getTransList() {
    $.getJSON(callListURL, function (data) {
        var items = [];
        $.each(data.calls, function (key, val) {
            var badge = levelBadge(val.caller_level),
                row = '<tr>' +
                    '<td class="mail-ontact">' + val.caller + '' +
                    '<span class="label label-' + badge.levelClass + ' pull-right">' + badge.levelText + '</span></td>' +
                    '<td class="mail-ontact"><strong>' + val.caller_number + '</strong></td>' +
                    '<td class="text-right mail-date">' + val.call_timestamps + '</td>' +
                    '<td class="text-right">' +
                    '<button class="btn btn-info btn-outline transButton"' +
                    'data-call_id="' + val.callid + '" ' +
                    'data-caller_id="' + val.caller_id + '" ' +
                    'data-caller="' + val.caller + '" ' +
                    'data-caller_level="' + val.caller_level + '" ' +
                    'data-caller_number="' + val.caller_number + '" ' +
                    'data-call_timestamps="' + val.call_timestamps + '" ' +
                    'data-audiofiles="' + val.audiofiles + '">' +
                    '<i class="fa fa-play"></i> Transcribe</button>' +
                    '</td>' +
                    '</tr>';

            items.push(row);
        });

        //Build the HTML
        $("<tbody/>", {
            "class": "call-list",
            html: items.join("")
        }).appendTo("#callTable");
    });
}

//Generate Registration List
function getRegistrationList() {
    $.getJSON(registrationListURL, function (data) {
        var items = [];
        $.each(data.registration, function (key, val) {
            row = '<tr class="read">' +
            '<td class="mail-ontact"><strong>' + val.caller_number + '</strong></td>' +
            '<td class="text-right mail-date">' + val.call_timestamps + '</td>' +
            '<td class="text-right">' +
            '<button class="btn btn-info btn-outline newRegistrationButton"' +
                'data-reg_request="1" ' +
                'data-call_id="' + val.callid + '" ' +
                'data-caller_number="' + val.caller_number + '" ' +
                'data-audiofiles="' + val.audiofiles + '">' +
            '<i class="fa fa-play"></i> Translate </button>' +
            '</td>' +
            '</tr>';
            items.push(row);
        });
        //Build the HTML
        $("<tbody/>", {
            "class": "registration-list",
            html: items.join("")
        }).appendTo("#registrationCallTable");
    });
}

//Generate Failed List
function getFailList() {
    $.getJSON(failListUrl, function (data) {
        var items = [];
        $.each(data.calls, function (key, val) {
            var badge = levelBadge(val.caller_level),
                row = '<tr>' +
                        '<td class="mail-ontact">' + val.caller + '' +
                        '<span class="label label-' + badge.levelClass + ' pull-right">' + badge.levelText + '</span></td>' +
                        '<td class="text-center"><strong>' + val.caller_number + '</strong></td>' +
                        '<td class="text-center mail-ontact">' + val.call_timestamps + '</td>' +
                        '<td class="text-center mail-ontact">' + val.tried_by_name + '</td>' +
                        '<td class="text-center mail-ontact">' + val.reason + '</td>' +
                        '<td class="text-left">' +
                            '<button class="btn btn-info listenButton"' +
                            'data-audiofiles="' + val.audiofiles + '">' +
                            '<i class="fa fa-play"></i> Audio </button>' +
                        '</td>' +
                        '<td class="text-left">' +
                            '<button class="btn btn-warning transButton pull-right"' +
                                'data-call_id="' + val.callid + '" ' +
                                'data-caller_id="' + val.caller_id + '" ' +
                                'data-caller="' + val.caller + '" ' +
                                'data-caller_level="' + val.caller_level + '" ' +
                                'data-caller_number="' + val.caller_number + '" ' +
                                'data-call_timestamps="' + val.call_timestamps + '" ' +
                                'data-audiofiles="' + val.audiofiles + '">' +
                                '<i class="fa fa-play"></i> Retry</button>' +
                        '</td>' +
                        '</tr>';

            items.push(row);
        });
        //Build the HTML
        $("<tbody/>", {
            "class": "fail-list",
            html: items.join("")
        }).appendTo("#failCallTable");

        $('#failCallTable thead').removeClass('hide');
    });
}

//Generate All Translation List
function getPreTransList() {
    $.getJSON(preTransListUrl, function (data) {
        var items = [];
        $.each(data.calls, function (key, val) {
            var badge = levelBadge(val.caller_level),
            row = '<tr>' +
                        '<td class="mail-ontact text-center">' + val.caller + '' +
                        '<span class="label label-' + badge.levelClass + ' pull-right">' + badge.levelText + '</span></td>' +
                        '<td class="mail-ontact text-center"><strong>' + val.caller_number + '</strong></td>' +
                        '<td class="mail-ontact text-center">' + val.call_timestamps + '</td>' +
                        '<td class="text-center">' + val.transaction_by + '</td>' +
                        '<td class="text-center">' +
                            '<button class="btn btn-info listenButton"' +
                            'data-audiofiles="' + val.audiofiles + '">' +
                            '<i class="fa fa-play"></i> Audio </button>' +
                        '</td>' +
                        '<td class="text-left">' +
                            '<button class="btn btn-warning preTranDetails pull-right"' +
                                'data-transaction_id="' + val.transaction_id + '">' +
                                '<i class="fa fa-play"></i> Transaction Details</button>' +
                        '</td>' +
                        '</tr>';
            items.push(row);
        });
        //Build the HTML
        $("<tbody/>", {
            "class": "pre-trans-list",
            html: items.join("")
        }).appendTo("#previousTranslationTable");
    });
}