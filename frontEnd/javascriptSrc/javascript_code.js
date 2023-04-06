$(document).ready(function () {

  $("#element-form").submit(async function (event) {
    console.log("Form submit triggered"); // Add this line
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

    try {
      const response = await $.ajax({
        url: "/element",
        method: "POST",
        processData: false,
        contentType: false,
        data: formData,
      });

      if (response.status === 200) {
        alert("Operation successful!");
      } else {
        alert("Error: " + response.statusText);
      }
    } catch (error) {
      alert("Error: " + error);
    }
  });
});