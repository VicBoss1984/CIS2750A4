$(document).ready(function () {

  $("#element-form").submit(async function (event) {
    event.preventDefault();

    const elementCode = $("#element_code").val();
    const elementName = $("#element_name").val();
    const operation = $('input[name="operation"]:checked').val();

    const formData = new FormData();
    if (typeof operation === "undefined") {
      alert("Please select an operation");
      return;
    }
    formData.append("element_code", elementCode);
    formData.append("element_name", elementName);
    formData.append("operation", operation);
    
    const response = await $.ajax({
      url: "/element",
      method: "POST",
      processData: "application/json",
      contentType: false,
      data: JSON.stringify({
        elementCode: elementCode,
        elementName: elementName,
        operation: operation
      }),
      success: function(response) { 
        console.log("Success! Response:", response);
      }, 
      error: function(xhr, status, error) { 
        console.error("Error! Status code:", xhr.status); 
        console.error("Error message:", error);
      }
    });
  });
});