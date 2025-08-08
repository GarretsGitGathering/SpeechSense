import 'dart:convert';
import 'dart:math';
import 'package:allen_dui_prevention/constants.dart';
import 'package:allen_dui_prevention/routePage.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'signUp.dart';

class SignInPage extends StatefulWidget {
  @override
  _SignInPageState createState() => _SignInPageState();
}

class _SignInPageState extends State<SignInPage> {
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  String errorMessage = "";
  bool _isLoading = false;

  // Sign In Function
  void signIn() async {
    String email = emailController.text.trim();
    String password = passwordController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      setState(() => errorMessage = "Email and password are required.");
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await customHttpClient.post(
        Uri.parse("$apiUrl/sign_in"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({
          "email": email,
          "password": password
        }),
      );

      setState(() => _isLoading = false);

      if (response.statusCode == 200) {
        final body = json.decode(response.body);
        if (body["user_id"] != null) {
          user_id = body["user_id"];
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => const RoutePage()),
          );
        } else {
          setState(() => errorMessage = "Invalid credentials. Please try again.");
        }
      } else {
        setState(() => errorMessage = "Error: ${response.reasonPhrase}");
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        errorMessage = "Error: $e";
      });
    }
  }

  // Generate and Save Anonymous ID
  Future<void> _continueAnonymously() async {
    setState(() => _isLoading = true);
    try {
      final prefs = await SharedPreferences.getInstance();
      String? storedId = prefs.getString('anonymous_user_id');

      if (storedId == null) {
        final deviceInfo = DeviceInfoPlugin();
        String uniqueId;

        if (Theme.of(context).platform == TargetPlatform.android) {
          var androidInfo = await deviceInfo.androidInfo;
          uniqueId = androidInfo.id;
        } else if (Theme.of(context).platform == TargetPlatform.iOS) {
          var iosInfo = await deviceInfo.iosInfo;
          uniqueId = iosInfo.identifierForVendor ?? Random().nextInt(100000).toString();
        } else {
          uniqueId = Random().nextInt(1000000).toString();
        }

        await prefs.setString('anonymous_user_id', uniqueId);
        user_id = uniqueId;
      } else {
        user_id = storedId;
      }

      setState(() => _isLoading = false);
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const RoutePage()),
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
        errorMessage = "Failed to generate anonymous ID.";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "SpeechSense",
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 30),

            // Email Input
            TextField(
              controller: emailController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: "Email",
                labelStyle: const TextStyle(color: Colors.white70),
                filled: true,
                fillColor: Colors.grey[900],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide.none,
                ),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 15),

            // Password Input
            TextField(
              controller: passwordController,
              obscureText: true,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: "Password",
                labelStyle: const TextStyle(color: Colors.white70),
                filled: true,
                fillColor: Colors.grey[900],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
            const SizedBox(height: 15),

            // Error Message
            if (errorMessage.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Text(
                  errorMessage,
                  style: const TextStyle(color: Colors.red, fontSize: 14),
                  textAlign: TextAlign.center,
                ),
              ),

            // Sign In Button
            ElevatedButton(
              onPressed: _isLoading ? null : signIn,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 14),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.black)
                  : const Text("Sign In"),
            ),
            const SizedBox(height: 10),

            // Anonymous Access Button
            ElevatedButton(
              onPressed: _isLoading ? null : _continueAnonymously,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[800],
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text("Continue Anonymously"),
            ),
            const SizedBox(height: 15),

            // Sign Up Link
            TextButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => SignUpPage()),
                );
              },
              child: const Text(
                "Don't have an account? Sign Up",
                style: TextStyle(color: Colors.white70),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
