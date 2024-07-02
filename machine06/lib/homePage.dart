import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class VideoPickerExample extends StatefulWidget {
  @override
  _VideoPickerExampleState createState() => _VideoPickerExampleState();
}

class _VideoPickerExampleState extends State<VideoPickerExample> {
  File? _video;
  String? _result;
  final picker = ImagePicker();

  Future pickVideo() async {
    final pickedFile = await picker.pickVideo(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _video = File(pickedFile.path);
      });
      uploadVideo(_video!);
    }
  }

  Future captureVideo() async {
    final pickedFile = await picker.pickVideo(source: ImageSource.camera);
    if (pickedFile != null) {
      setState(() {
        _video = File(pickedFile.path);
      });
      uploadVideo(_video!);
    }
  }

  Future<void> uploadVideo(File videoFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('http://192.168.0.125:5000/upload'), // Use 10.0.2.2 for Android Emulator, or your local IP for a physical device
    );
    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        videoFile.path,
      ),
    );
    var response = await request.send();
    if (response.statusCode == 200) {
      var responseData = await response.stream.bytesToString();
      var jsonResponse = json.decode(responseData);
      setState(() {
        _result = jsonResponse['result'].toStringAsFixed(2); // Ensure result is a String
      });
    } else {
      setState(() {
        _result = 'Upload failed with status: ${response.statusCode}';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Heart Rate'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            ElevatedButton(
              onPressed: pickVideo,
              child: Text('Pick Video from Gallery'),
            ),
            ElevatedButton(
              onPressed: captureVideo,
              child: Text('Capture Video from Camera'),
            ),
            if (_video == null) Text('No video selected.'),
            _result == null
                ? Container()
                : Text('Result: $_result'),
          ],
        ),
      ),
    );
  }
}
