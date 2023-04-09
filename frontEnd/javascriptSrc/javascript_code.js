$(document).ready(function () {

  $("#element-form").submit(async function (event) {
    event.preventDefault();

    const elementCode = $("#element_code").val();
    const elementName = $("#element_name").val();
    const elementNum = $("#element_num").val();
    const elementRadius = $("#element_radius").val();
    const elementCol1 = $("#element_col1").val();
    const elementCol2 = $("#element_col2").val();
    const elementCol3 = $("#element_col3").val();
    const operation = $('input[name="operation"]:checked').val();

    const formData = new FormData();
    if (typeof operation === "undefined") {
      alert("Please select an operation");
      return;
    }
    formData.append("element_code", elementCode);
    formData.append("element_name", elementName);
    formData.append("element_num", elementNum);
    formData.append("element_radius", elementRadius);
    formData.append("element_col1", elementCol1);
    formData.append("element_col2", elementCol2);
    formData.append("element_col3", elementCol3);
    formData.append("operation", operation);
    
    const response = await $.ajax({
      url: "/element",
      method: "POST",
      processData: "application/json",
      contentType: false,
      data: JSON.stringify({
        elementCode: elementCode,
        elementName: elementName,
        elementNum: elementNum,
        elementRadius: elementRadius,
        elementCol1: elementCol1,
        elementCol2: elementCol2,
        elementCol3: elementCol3,
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