exports.handler = function(event, context) {
  // Configure the email domain that will be allowed to automatically verify.
  var approvedDomain = "ianduffy.ie";

  // Log the event information for debugging purposes.
  console.log("Received event:", JSON.stringify(event, null, 2));
  if (event.request.userAttributes.email.includes("@" + approvedDomain)) {
    console.log(
      "This is an approved email address. Proceeding to send verification email."
    );
    context.done(null, event);
  } else {
    console.log("This is not an approved email address. Throwing error.");
    var error = new Error("the supplied email address does not have access to this service.");
    context.done(error, event);
  }
};
