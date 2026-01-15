// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'type.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$TabType {

 String get key; Widget get title; Widget get content;
/// Create a copy of TabType
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TabTypeCopyWith<TabType> get copyWith => _$TabTypeCopyWithImpl<TabType>(this as TabType, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TabType&&(identical(other.key, key) || other.key == key)&&(identical(other.title, title) || other.title == title)&&(identical(other.content, content) || other.content == content));
}


@override
int get hashCode => Object.hash(runtimeType,key,title,content);

@override
String toString() {
  return 'TabType(key: $key, title: $title, content: $content)';
}


}

/// @nodoc
abstract mixin class $TabTypeCopyWith<$Res>  {
  factory $TabTypeCopyWith(TabType value, $Res Function(TabType) _then) = _$TabTypeCopyWithImpl;
@useResult
$Res call({
 String key, Widget title, Widget content
});




}
/// @nodoc
class _$TabTypeCopyWithImpl<$Res>
    implements $TabTypeCopyWith<$Res> {
  _$TabTypeCopyWithImpl(this._self, this._then);

  final TabType _self;
  final $Res Function(TabType) _then;

/// Create a copy of TabType
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? key = null,Object? title = null,Object? content = null,}) {
  return _then(_self.copyWith(
key: null == key ? _self.key : key // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as Widget,content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as Widget,
  ));
}

}


/// Adds pattern-matching-related methods to [TabType].
extension TabTypePatterns on TabType {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TabType value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TabType() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TabType value)  $default,){
final _that = this;
switch (_that) {
case _TabType():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TabType value)?  $default,){
final _that = this;
switch (_that) {
case _TabType() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String key,  Widget title,  Widget content)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TabType() when $default != null:
return $default(_that.key,_that.title,_that.content);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String key,  Widget title,  Widget content)  $default,) {final _that = this;
switch (_that) {
case _TabType():
return $default(_that.key,_that.title,_that.content);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String key,  Widget title,  Widget content)?  $default,) {final _that = this;
switch (_that) {
case _TabType() when $default != null:
return $default(_that.key,_that.title,_that.content);case _:
  return null;

}
}

}

/// @nodoc


class _TabType implements TabType {
  const _TabType({required this.key, required this.title, required this.content});
  

@override final  String key;
@override final  Widget title;
@override final  Widget content;

/// Create a copy of TabType
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TabTypeCopyWith<_TabType> get copyWith => __$TabTypeCopyWithImpl<_TabType>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _TabType&&(identical(other.key, key) || other.key == key)&&(identical(other.title, title) || other.title == title)&&(identical(other.content, content) || other.content == content));
}


@override
int get hashCode => Object.hash(runtimeType,key,title,content);

@override
String toString() {
  return 'TabType(key: $key, title: $title, content: $content)';
}


}

/// @nodoc
abstract mixin class _$TabTypeCopyWith<$Res> implements $TabTypeCopyWith<$Res> {
  factory _$TabTypeCopyWith(_TabType value, $Res Function(_TabType) _then) = __$TabTypeCopyWithImpl;
@override @useResult
$Res call({
 String key, Widget title, Widget content
});




}
/// @nodoc
class __$TabTypeCopyWithImpl<$Res>
    implements _$TabTypeCopyWith<$Res> {
  __$TabTypeCopyWithImpl(this._self, this._then);

  final _TabType _self;
  final $Res Function(_TabType) _then;

/// Create a copy of TabType
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? key = null,Object? title = null,Object? content = null,}) {
  return _then(_TabType(
key: null == key ? _self.key : key // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as Widget,content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as Widget,
  ));
}


}

// dart format on
