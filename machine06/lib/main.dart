import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:machine06/auth/login.dart';
import 'package:machine06/auth/signup.dart';
import 'package:machine06/homePage.dart';
import 'package:firebase_core/firebase_core.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: FirebaseAuth.instance.currentUser == null ? const Login() : VideoPickerExample(),
      routes: {
        "signup" : (context) => const SignUp(),
        "login" : (context) => const Login(),
        "homepage" : (context) => VideoPickerExample(),
      },
    );
  }
}