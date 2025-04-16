from .recruitment import fp_group

def register_commands(client):
    print("Registering commands...")
    client.tree.add_command(fp_group)
    print(f"Registered command group: {fp_group.name}")
    
__all__ = ["register_commands"]