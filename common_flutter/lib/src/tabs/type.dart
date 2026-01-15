// import 'package:flutter/widgets.dart';
import 'package:flutter/material.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'type.freezed.dart';
// part 'type.g.dart';

@freezed
abstract class TabType with _$TabType {
  const factory TabType({
    required String key,
    required Widget title,
    required Widget content,
  }) = _TabType;
}

// @freezed
// abstract class Person with _$Person {
//   const factory Person({
//     required String firstName,
//     required String lastName,
//     required int age,
//   }) = _Person;

//   factory Person.fromJson(Map<String, Object?> json) => _$PersonFromJson(json);
// }
