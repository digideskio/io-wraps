#!/usr/bin/python2.6
#
# Copyright 2010 Google Inc. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Java library generator.

Specializations to the code Generator for Java bindings. This class also serves
as a superclass for GWT generation, since that shares Java's naming rules.
"""

__author__ = 'aiuto@google.com (Tony Aiuto)'

from googleapis.codegen import api
from googleapis.codegen import generator
from googleapis.codegen import template_objects
from googleapis.codegen import utilities
from googleapis.codegen.import_definition import ImportDefinition
from googleapis.codegen.java_import_manager import JavaImportManager
from googleapis.codegen.language_model import LanguageModel


class JavaGenerator(generator.ApiLibraryGenerator):
  """The Java code generator."""

  def __init__(self, discovery, language='java', language_model=None,
               options=dict()):
    if not language_model:
      language_model = JavaLanguageModel()
    super(JavaGenerator, self).__init__(JavaApi, discovery, language,
                                        language_model, options=options)

  def AnnotateApi(self, the_api):
    """Annotate the Api dictionary with Java specifics."""

    # Create packages where code lives.
    package_path = 'com/google/api/services/%s' % the_api.values['name']
    if self._options.get('version_package'):
      package_path = '%s/%s' % (package_path, the_api.values['versionNoDots'])
    self._package = template_objects.Package(package_path,
                                             language_model=self.language_model)
    the_api.SetTemplateValue('package', self._package)
    self._model_package = template_objects.Package('model',
                                                   parent=self._package)

  def AnnotateMethod(self, the_api, method, resource):
    """Annotate a Method with Java specific elements.

    We add a few things:
    * Annotate our parameters
    * Constructor declaration lists.  We do it here rather than in a template
      mainly because it is much easier to do the join around the ','
    * Add a 'content' member for PUT/POST methods which take an object as input.

    Args:
      the_api: (Api) The API tree which owns this method.
      method: (Method) The method to annotate.
      resource: (Resource) The resource which owns this method.
    """
    # Chain up so our parameters are annotated first.
    super(JavaGenerator, self).AnnotateMethod(the_api, method, resource)

  def AnnotateParameter(self, unused_method, parameter):
    """Annotate a Parameter with Java specific elements."""
    self._HandleImports(parameter)

  def AnnotateProperty(self, unused_api, prop, unused_schema):
    """Annotate a Property with Java specific elements."""
    self._HandleImports(prop)

  def _HandleImports(self, element):
    """Handles imports for the specified element.

    Args:
      element: (Property|Parameter) The property we want to set the import for.
    """
    # Get the parent of this Property/Parameter.
    parent = element.schema
    import_manager = JavaImportManager.GetCachedImportManager(parent)

    def_dict = element.values
    json_type = def_dict.get('type', 'string')
    json_format = def_dict.get('format')
    type_format_to_datatype_and_imports = self.language_model.type_map
    datatype_and_imports = (
        type_format_to_datatype_and_imports.get((json_type, json_format)))
    if datatype_and_imports:
      import_definition = datatype_and_imports[1]
      # Import all required imports.
      for required_import in import_definition.imports:
        import_manager.AddImport(required_import)
      # Set all template values, if specified.
      for template_value in import_definition.template_values:
        element.SetTemplateValue(template_value, True)


class JavaLanguageModel(LanguageModel):
  """A LanguageModel tuned for Java."""

  _JSON_STRING_IMPORT = 'com.google.api.client.json.JsonString'
  _JSON_STRING_TEMPLATE_VALUE = 'requiresJsonString'

  # Dictionary of json type and format to its corresponding data type and
  # import definition. The first import in the imports list is the primary
  # import.
  TYPE_FORMAT_TO_DATATYPE_AND_IMPORTS = {
      ('boolean', None): ('Boolean', ImportDefinition(['java.lang.Boolean'])),
      ('any', None): ('Object', ImportDefinition(['java.lang.Object'])),
      ('integer', 'int16'): ('Short', ImportDefinition(['java.lang.Short'])),
      ('integer', 'int32'): ('Integer',
                             ImportDefinition(['java.lang.Integer'])),
      # Java does not support Unsigned Integers
      ('integer', 'uint32'): ('Long', ImportDefinition(['java.lang.Long'])),
      ('number', 'double'): ('Double', ImportDefinition(['java.lang.Double'])),
      ('number', 'float'): ('Float', ImportDefinition(['java.lang.Float'])),
      ('object', None): ('Object', ImportDefinition(['java.lang.Object'])),
      ('string', None): ('String', ImportDefinition(['java.lang.String'])),
      ('string', 'byte'): ('String', ImportDefinition(['java.lang.String'])),
      ('string', 'date-time'): ('DateTime', ImportDefinition(
          ['com.google.api.client.util.DateTime'])),
      ('string', 'int64'): ('Long', ImportDefinition(
          ['java.lang.Long', _JSON_STRING_IMPORT],
          [_JSON_STRING_TEMPLATE_VALUE])),
      # Java does not support Unsigned Integers
      ('string', 'uint64'): ('BigInteger', ImportDefinition(
          ['java.math.BigInteger', _JSON_STRING_IMPORT],
          [_JSON_STRING_TEMPLATE_VALUE])),
      }

  _JAVA_KEYWORDS = [
      'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
      'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
      'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements',
      'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new',
      'package', 'private', 'protected', 'public', 'return', 'short', 'static',
      'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
      'transient', 'try', 'void', 'volatile', 'while'
      ]

  # We can not create classes which match a Java keyword or built in object
  # type.
  RESERVED_CLASS_NAMES = _JAVA_KEYWORDS + [
      'float', 'integer', 'object', 'string', 'true', 'false',
      ]

  def __init__(self):
    super(JavaLanguageModel, self).__init__(class_name_delimiter='.')
    self._type_map = JavaLanguageModel.TYPE_FORMAT_TO_DATATYPE_AND_IMPORTS

  @property
  def type_map(self):
    return self._type_map

  def GetCodeTypeFromDictionary(self, def_dict):
    """Convert a json schema type to a suitable Java type name.

    Overrides the default.

    Args:
      def_dict: (dict) A dictionary describing Json schema for this Property.
    Returns:
      A name suitable for use as a class in the generator's target language.
    """
    json_type = def_dict.get('type', 'string')
    json_format = def_dict.get('format')

    datatype_and_imports = self._type_map.get((json_type, json_format))
    if datatype_and_imports:
      # If there is an entry in the type format to datatype and imports
      # dictionary set it as the native format.
      native_format = datatype_and_imports[0]
    else:
      # Could not find it in the dictionary, set it to the json type.
      native_format = utilities.CamelCase(json_type)
    return native_format

  def CodeTypeForArrayOf(self, type_name):
    """Take a type name and return the syntax for an array of them.

    Overrides the default.

    Args:
      type_name: (str) A type name.
    Returns:
      A language specific string meaning "an array of type_name".
    """
    return 'java.util.List<%s>' % type_name

  def CodeTypeForMapOf(self, type_name):
    """Take a type name and return the syntax for a map of String to them.

    Overrides the default.

    Args:
      type_name: (str) A type name.
    Returns:
      A language specific string meaning "an array of type_name".
    """
    return 'java.util.Map<String, %s>' % type_name

  def ToMemberName(self, s, the_api):
    """CamelCase a wire format name into a suitable Java variable name."""
    camel_s = utilities.CamelCase(s)
    if s.lower() in JavaLanguageModel.RESERVED_CLASS_NAMES:
      # Prepend the service name
      return '%s%s' % (the_api.values['name'], camel_s)
    return camel_s[0].lower() + camel_s[1:]


class JavaApi(api.Api):
  """An Api with Java annotations."""

  def __init__(self, discovery_doc, **unused_kwargs):
    super(JavaApi, self).__init__(discovery_doc)

  def ToClassName(self, s, element_type=None):
    """Convert a discovery name to a suitable Java class name.

    In Java, nested class names cannot share the same name as the outer class
    name.

    Overrides the default.

    Args:
      s: (str) A rosy name of data element.
      element_type: (str) The kind of object we need a class name for.
    Returns:
      A name suitable for use as a class in the generator's target language.
    """
    if s.lower() in JavaLanguageModel.RESERVED_CLASS_NAMES:
      # Prepend the service name
      return '%s%s' % (utilities.CamelCase(self.values['name']),
                       utilities.CamelCase(s))

    name = utilities.CamelCase(s)
    if name == self.values.get('className'):
      if 'resource' == element_type:
        name += 'Operations'
      elif 'method' == element_type:
        name += 'Operation'
    return name
