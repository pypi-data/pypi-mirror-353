from pdfco.mcp.server import mcp
from pdfco.mcp.tools.apis import conversion, job, file, modification, form, search, searchable, security, document, extraction, editing
    
def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
