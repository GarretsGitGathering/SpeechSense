import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:allen_dui_prevention/constants.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  // Function to open the account deletion request form
  void _launchDeletionForm() async {
    final Uri formUrl = Uri.parse("https://docs.google.com/forms/d/e/1FAIpQLScrQ_Dutzi5I3sXWuQOvDoq_MNz672Z6Po57cA7IE1oN2Rdwg/viewform?usp=header");  // Replace with the actual form URL
    if (await canLaunchUrl(formUrl)) {
      await launchUrl(formUrl);
    } else {
      throw "Could not launch $formUrl";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Settings"),
        centerTitle: true,
        backgroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Account Information",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[900],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    "User ID:",
                    style: TextStyle(fontSize: 16, color: Colors.white70),
                  ),
                  Text(
                    user_id!,  // Displaying user_id from constants.dart
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ],
              ),
            ),
            const Spacer(), // Pushes the deletion link to the bottom
            Center(
              child: GestureDetector(
                onTap: _launchDeletionForm,
                child: const Text(
                  "Request Account Deletion",
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.red,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
      backgroundColor: Colors.white,
    );
  }
}
