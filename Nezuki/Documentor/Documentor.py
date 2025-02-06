import ast
import os
from typing import List, Dict, Any

class Documentor:
    """Classe che genera la documentazione in formato Markdown dei file Python, aggiornando anche il file README.md che si trova nel progetto principale, fornendo indicazioni sulle deprecazioni."""
    
    def __init__(self, directory_path: str) -> None:
        """Inizializza l'oggetto Documentor.
        
        Args:
            directory_path (str): Il percorso della directory contenente i file Python da documentare.
        """
        self.directory_path = directory_path
        self.deprecations: List[Dict[str, Any]] = []
        self.class_docs: List[Dict[str, Any]] = []

    def document_all_modules(self) -> None:
        """Genera la documentazione per tutti i file Python nella directory specificata."""
        for filename in os.listdir(self.directory_path):
            if filename.endswith(".py"):
                module_path = os.path.join(self.directory_path, filename)
                self.document_module(module_path)
        self.write_readme()

    def document_module(self, module_path: str) -> None:
        """Legge il contenuto di un file Python e avvia il processo di analisi del codice per generare la documentazione Markdown.
        
        Args:
            module_path (str): Il percorso del file Python da documentare.
        """
        with open(module_path, 'r') as file:
            source_code = file.read()

        tree = ast.parse(source_code, filename=module_path)
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        for class_node in classes:
            class_info = self.extract_info(class_node, source_code)
            markdown = self.generate_markdown(class_info)
            self.write_markdown_to_file(markdown, class_info['name'])
            self.class_docs.append(class_info)

    def extract_info(self, class_node: ast.ClassDef, source_code: str) -> Dict[str, Any]:
        """Estrae informazioni da una definizione di classe nel codice sorgente.
        
        Args:
            class_node (ast.ClassDef): Nodo AST della classe.
            source_code (str): Il codice sorgente del modulo.
        
        Returns:
            Dict[str, Any]: Un dizionario contenente informazioni sulla classe, come il nome, la docstring, gli attributi, i metodi e la versione.
        """
        info: Dict[str, Any] = {
            'name': class_node.name,
            'docstring': ast.get_docstring(class_node) or "No documentation provided.",
            'attributes': [],
            'methods': [],
            'version': self.extract_version(class_node)
        }

        # Check if the class is deprecated
        deprecation_info = self.extract_deprecation(class_node)
        if deprecation_info['version']:
            self.deprecations.append({
                'class': info['name'],
                'method': '',
                'version': deprecation_info['version'],
                'reason': deprecation_info['reason']
            })

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_info = self.extract_method_info(node, source_code)
                info['methods'].append(method_info)
                if method_info['deprecated_from']:
                    self.deprecations.append({
                        'class': info['name'],
                        'method': method_info['name'],
                        'version': method_info['deprecated_from'],
                        'reason': method_info['deprecated_reason']
                    })
            elif isinstance(node, ast.AnnAssign):  # Assegnazioni annotate
                attribute_info = {
                    'name': node.target.id if isinstance(node.target, ast.Name) else "Unknown",
                    'type': ast.unparse(node.annotation) if node.annotation else "Unknown"
                }
                info['attributes'].append(attribute_info)
            elif isinstance(node, ast.Assign):  # Assegnazioni semplici
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        attribute_info = {
                            'name': target.id,
                            'type': "Unknown"  # Non c'è annotazione esplicita in `Assign`
                        }
                        info['attributes'].append(attribute_info)

        return info

    def generate_markdown(self, info: Dict[str, Any]) -> str:
        """Genera la documentazione in formato Markdown a partire dalle informazioni della classe.
        
        Args:
            info (Dict[str, Any]): Un dizionario contenente informazioni sulla classe.
        
        Returns:
            str: La documentazione in formato Markdown.
        """
        markdown = [f"# {info['name']}\n"]
        markdown.append(f"**Version**: {info['version']}\n\n")
        markdown.append(info['docstring'] + "\n\n")

        # Table of Contents
        markdown.append("## Table of Contents\n")
        markdown.append("- [Introduction](#introduction)\n")
        if info['attributes']:
            markdown.append("- [Attributes](#attributes)\n")
        if info['methods']:
            markdown.append("- [Methods](#methods)\n")
            for method in info['methods']:
                if method.get('deprecated_from'):
                    markdown.append(f"  - **⚠️ Deprecation** [{method['name']}](#{method['name'].lower().replace(' ', '-')})\n")
                else:
                    markdown.append(f"  - [{method['name']}](#{method['name'].lower().replace(' ', '-')})\n")

        # Attributes
        if info['attributes']:
            markdown.append("\n## Attributes\n")
            markdown.append("| Name | Type |\n| --- | --- |\n")
            for attr in info['attributes']:
                markdown.append(f"| {attr['name']} | {attr['type']} |\n")
            markdown.append("\n")

        # Methods
        if info['methods']:
            markdown.append("\n## Methods\n")
            for method in info['methods']:
                if method.get('deprecated_from'):
                    markdown.append(f"### ⚠️ {method['name']} - __deprecation__\n")
                else:
                    markdown.append(f"### {method['name']}\n")
                markdown.append(f"{method['docstring']}\n")
                if method.get('deprecated_from'):
                    markdown.append(f"\n**⚠️ DEPRECATION**: \n\n- Dalla versione {method['deprecated_from']}\n\n- Motivo/Alternativa: {method['deprecated_reason']} \n\n")
                markdown.append("\n#### Input\n")
                markdown.append("| Name | Type |\n| --- | --- |\n")
                for arg in method['arguments']:
                    markdown.append(f"| {arg[0]} | {arg[1]} |\n")
                markdown.append(f"\n#### Output\n{method['return']}\n\n")
                markdown.append("**Code**:\n\n")
                markdown.append("```python\n" + method['code'] + "\n```\n\n")

        return "".join(markdown)

    def extract_method_info(self, node: ast.FunctionDef, source_code: str) -> Dict[str, Any]:
        """Estrae informazioni da una definizione di metodo nel codice sorgente.
        
        Args:
            node (ast.FunctionDef): Nodo AST del metodo.
            source_code (str): Il codice sorgente del modulo.
        
        Returns:
            Dict[str, Any]: Un dizionario contenente informazioni sul metodo, come il nome, la docstring, gli argomenti, il tipo di ritorno, la deprecazione e il codice sorgente.
        """
        args = [(arg.arg, ast.unparse(arg.annotation) if arg.annotation else "Unknown") for arg in node.args.args]
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "No documentation provided.",
            'arguments': args,
            'return': self.extract_return_annotation(node),
            'deprecated_from': self.extract_deprecation(node)['version'],
            'deprecated_reason': self.extract_deprecation(node)['reason'],
            'code': ast.get_source_segment(source_code, node) or "No code available"
        }

    def extract_return_annotation(self, node: ast.FunctionDef) -> str:
        """Estrae l'annotazione di ritorno di un metodo.
        
        Args:
            node (ast.FunctionDef): Nodo AST del metodo.
        
        Returns:
            str: L'annotazione di ritorno del metodo.
        """
        if node.returns:
            return ast.unparse(node.returns)
        return "None"

    def extract_deprecation(self, node: ast.AST) -> Dict[str, str]:
        """Estrae informazioni di deprecazione da una definizione di funzione o classe.
        
        Args:
            node (ast.AST): Nodo AST della funzione o classe.
        
        Returns:
            Dict[str, str]: Un dizionario contenente la versione di deprecazione e il motivo della deprecazione.
        """
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and getattr(decorator.func, 'id', '') == 'deprecated':
                if len(decorator.args) > 1:
                    version = ast.unparse(decorator.args[0])
                    reason = ast.unparse(decorator.args[1])
                    return {"version": version, "reason": reason}
        return {"version": None, "reason": None}
    
    def extract_version(self, class_node: ast.ClassDef) -> str:
        """Estrae la versione di una classe.
        
        Args:
            class_node (ast.ClassDef): Nodo AST della classe.
        
        Returns:
            str: La versione della classe.
        """
        for decorator in class_node.decorator_list:
            if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'id') and decorator.func.id == 'versione':
                if decorator.args:
                    return ast.unparse(decorator.args[0])
        return "Unknown"

    def write_markdown_to_file(self, markdown: str, class_name: str)-> None:
        """ Scrive la documentazione Markdown in un file. 
        
            Args:
                - markdown (str): La documentazione in formato Markdown.
                - class_name (str): Il nome della classe.
        """
        file_path = os.path.join(self.directory_path, f"{class_name}.md")
        with open(file_path, 'w') as file:
            file.write(markdown)

    def write_readme(self) -> None:
        """Scrive il file README.md con le informazioni delle deprecazioni e dei moduli."""
        readme_path = os.path.join(self.directory_path, "..", "README.md")
        with open(readme_path, 'w') as file:
            file.write("# Project Documentation\n\n")
            file.write("## Deprecations\n")
            file.write("| Class | Method | Deprecated From | Reason |\n")
            file.write("| --- | --- | --- | --- |\n")
            for dep in self.deprecations:
                if dep['method'] == "":
                    file.write(f"| {dep['class']} | _Tutto il modulo_ | {dep['version']} | {dep['reason']} |\n")
                else:
                    file.write(f"| {dep['class']} | {dep['method']} | {dep['version']} | {dep['reason']} |\n")
            file.write("\n## Modules\n")
            for class_info in self.class_docs:
                file.write(f"- [{class_info['name']}]({class_info['name']}.md): {class_info['docstring'].splitlines()[0]}\n")

# Example usage:
documentor = Documentor(os.path.dirname(__file__))
documentor.document_all_modules()