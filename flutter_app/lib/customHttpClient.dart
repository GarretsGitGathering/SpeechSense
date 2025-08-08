import 'package:http/http.dart' as http;
import 'package:http/io_client.dart';
import 'dart:io';

// Custom HttpClient that ignores SSL certificate validation
class CustomHttpClient extends http.BaseClient {
  final http.Client _inner;

  CustomHttpClient() : _inner = IOClient(HttpClient()
    ..badCertificateCallback = (X509Certificate cert, String host, int port) => true);

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) {
    return _inner.send(request);
  }
}