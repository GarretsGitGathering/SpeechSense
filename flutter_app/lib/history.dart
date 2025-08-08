import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:audioplayers/audioplayers.dart';
import 'package:allen_dui_prevention/constants.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  List<Map<dynamic, dynamic>> _history = [];
  bool _isLoading = true;
  String? _errorMessage;
  final AudioPlayer _audioPlayer = AudioPlayer();

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  // Fetch history from the backend
  Future<void> _fetchHistory() async {
    try {
      final response = await customHttpClient.post(
        Uri.parse('$apiUrl/get_history'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"user_id": user_id}),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200 && data["data"] != null) {
        setState(() {
          _history = (data["data"] as Map<String, dynamic>).entries.map((entry) {
            return {"timestamp": entry.key, ...entry.value};
          }).toList();
          _isLoading = false;
        });
      } else {
        setState(() {
          _isLoading = false;
          _errorMessage = "Error: ${response.reasonPhrase}";
          print(_errorMessage);
        });
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = "Error fetching history.";
      });
    }
  }

  // Fetch signed URL for audio playback
  Future<void> _playAudio(String filePath) async {
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/download_audio'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"user_id": user_id, "file_path": filePath}),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200 && data["url"] != null) {
        print("Video URL: ${data["url"]}");
        await _audioPlayer.play(UrlSource(data["url"]));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Error fetching audio URL.")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to play audio.")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("History", style: TextStyle(color: Colors.black),),
        centerTitle: true,
        backgroundColor: Colors.white,
        automaticallyImplyLeading: false,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _history.isEmpty
          ? const Center(child: Text("No history available.", style: TextStyle(color: Colors.white)))
          : ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _history.length,
        itemBuilder: (context, index) {
          final record = _history[index];
          final isIntoxicated = record["is_intoxicated"] ?? false;
          final script = record["script"] ?? "Unknown script";
          final timestamp = DateTime.fromMillisecondsSinceEpoch(
              (double.parse(record["timestamp"]) * 1000).toInt());

          return Card(
            color: Colors.grey[900],
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Date: ${timestamp.toLocal()}",
                    style: const TextStyle(fontSize: 16, color: Colors.white),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Script: $script",
                    style: const TextStyle(fontSize: 14, color: Colors.white70),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Result: ${isIntoxicated ? "Impaired" : "Clear"}",
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: isIntoxicated ? Colors.red : Colors.green,
                    ),
                  ),
                  const SizedBox(height: 10),
                  ElevatedButton(
                    onPressed: () => _playAudio(record["audio_recording"]),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                    ),
                    child: const Text("Play Audio"),
                  ),
                ],
              ),
            ),
          );
        },
      ),
      backgroundColor: Colors.white,
    );
  }
}
