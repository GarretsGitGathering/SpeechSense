import 'dart:convert';
import 'dart:io';

import 'package:allen_dui_prevention/Analyze/resultsPage.dart';
import 'package:allen_dui_prevention/constants.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

class ScriptPage extends StatefulWidget {
  const ScriptPage({super.key});

  @override
  State<ScriptPage> createState() => _ScriptPageState();
}

class _ScriptPageState extends State<ScriptPage> {
  String _scriptText = "Fetching Script...";
  bool _isRecording = false;
  bool _isRecorderReady = false;
  late FlutterSoundRecorder _recorder;
  String? _audioFilePath;

  @override
  void initState() {
    super.initState();
    _recorder = FlutterSoundRecorder();
    _initRecorder();
    _fetchScript();
  }

  Future<void> _fetchScript() async {
    try {
      final response = await http.post(
          Uri.parse('$apiUrl/get_script'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({"user_id": user_id})
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _scriptText = data["script"] ?? "No script received.";
        });
      } else {
        setState(() {
          _scriptText = "Error fetching script.";
        });
      }
    } catch (e) {
      setState(() {
        _scriptText = "Error getting script.";
      });
    }
  }

  // Function to show an alert dialog explaining to the user
  Future<void> showSettingsDialog(BuildContext context) async {
    return showDialog<void>(
      context: context,
      barrierDismissible: false, // Prevent dismissing by tapping outside
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Microphone Permission Denied'),
          content: const Text(
            'To continue using the microphone, you need to enable microphone permissions in your settings. '
                'Would you like to go there now and enable it?',
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close the dialog
              },
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                openAppSettings(); // Open app settings
                Navigator.of(context).pop(); // Close the dialog
              },
              child: const Text('Go to Settings', style: TextStyle(color: Colors.black)),
            ),
          ],
        );
      },
    );
  }

  // Updated _initRecorder function with alert dialog
  Future<void> _initRecorder() async {
    // Request microphone permission
    var status = await Permission.microphone.request();

    if (status.isGranted) {
      // Initialize the recorder if permission is granted
      await _recorder.openRecorder();
      _recorder.setSubscriptionDuration(const Duration(milliseconds: 500));

      setState(() {
        _isRecorderReady = true;
      });
    } else if (status.isDenied) {
      // Permission denied, show a message
      setState(() {
        _scriptText = "Microphone permission denied. Please enable it in settings.";
      });
    } else if (status.isPermanentlyDenied) {
      // If permission is permanently denied, show dialog to go to settings
      showSettingsDialog(context);
      setState(() {
        _scriptText = "Microphone permission permanently denied. Please enable it in settings.";
      });
    } else if (status.isRestricted) {
      // If permission is restricted (e.g., parental controls)
      setState(() {
        _scriptText = "Microphone access is restricted. Please check your settings.";
      });
    }
  }

  Future<void> _startRecording() async {
    try {
      if (!_isRecorderReady) {
        print("Recorder was NOT ready!");
        return;
      }

      final dir = await getApplicationDocumentsDirectory();
      _audioFilePath = "${dir.path}/recording.wav";

      await _recorder.startRecorder(
        toFile: _audioFilePath,
        codec: Codec.pcm16WAV,
        audioSource: AudioSource.microphone
      );

      setState(() {
        _isRecording = true;
      });
    } catch (e) {
      print("Error starting recording: $e");
    }
  }

  Future<void> _stopRecording() async {
    try {
      await _recorder.stopRecorder();

      setState(() {
        _isRecording = false;
      });

      print("Recording saved at: $_audioFilePath");

      // push to the resultPage
      if (_audioFilePath != null) {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => ResultsPage(audioFilePath: _audioFilePath!, script: _scriptText,)),
        );
      }
    } catch (e) {
      print("Error stopping recording: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        backgroundColor: Colors.black,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              "Press 'Start Recording' to record yourself reading the text.",
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 20, color: Colors.white),
            ),
            SizedBox(height: 30),
            Text(
              _scriptText,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 18, color: Colors.orangeAccent),
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: _isRecording ? _stopRecording : _startRecording,
              style: ElevatedButton.styleFrom(
                backgroundColor: _isRecording ? Colors.red : Colors.white,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              child: Text(_isRecording ? "Stop Recording" : "Start Recording"),
            ),
          ],
        ),
      ),
      backgroundColor: Colors.black,
    );
  }
}
