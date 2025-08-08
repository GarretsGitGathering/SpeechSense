import 'dart:convert';
import 'dart:io';

import 'package:allen_dui_prevention/customHttpClient.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../constants.dart';

class ResultsPage extends StatefulWidget {
  const ResultsPage({super.key, required this.audioFilePath, required this.script});
  final String audioFilePath;
  final String script;

  @override
  State<ResultsPage> createState() => _ResultsPageState();
}

class _ResultsPageState extends State<ResultsPage> {
  String _analysisResult = "Uploading audio...";
  bool _isUploading = true;

  @override
  void initState() {
    super.initState();
    _uploadAudio(File(widget.audioFilePath));
  }

  // Function to upload the audio file to the backend
  Future<void> _uploadAudio(File audioFile) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$apiUrl/get_prediction'))
        ..fields['user_id'] = user_id!
        ..fields['script'] = widget.script
        ..files.add(await http.MultipartFile.fromPath('file', audioFile.path));

      print(user_id!);
      print(widget.script);
      print(audioFile.path);

      print("Sending request...");
      var response = await customHttpClient.send(request);

      if (response.statusCode == 200){
        setState(() {
          _isUploading = false;
          _analysisResult ="Audio Processing. Check your History page for your result shortly";
        });
      }else{
        setState(() {
          _isUploading = false;
          _analysisResult = "Failed to analyze speech. Error: ${response.toString()}";
          print("Error: ${response.reasonPhrase}");
        });
      }
    } catch (e) {
      setState(() {
        _isUploading = false;
        _analysisResult = "Error processing audio.";
      });
      print("Error uploading audio: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        backgroundColor: Colors.black,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                "Analyzing Speech...",
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 20),
              _isUploading
                  ? const CircularProgressIndicator()
                  : Text(
                _analysisResult,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 18, color: Colors.white70),
              ),
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
      backgroundColor: Colors.black,
    );
  }
}
