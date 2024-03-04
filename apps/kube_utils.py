role_template = """
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: {namespace}
  name: {role_name}
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "watch", "list", "create", "delete"]
"""

role_binding_template = """
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {role_binding_name}
  namespace: {namespace}
subjects:
- kind: User
  name: {username}
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: {role_name}
  apiGroup: rbac.authorization.k8s.io
"""

def get_role_yaml(namespace, role_name):
    return role_template.format(namespace=namespace, role_name=role_name)

def get_role_binding_yaml(namespace, role_binding_name, username, role_name):
    return role_binding_template.format(
        namespace=namespace, role_binding_name=role_binding_name,
        username=username, role_name=role_name)