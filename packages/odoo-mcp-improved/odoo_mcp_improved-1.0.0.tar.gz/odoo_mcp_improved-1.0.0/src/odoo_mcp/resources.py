"""
Integración de recursos para MCP-Odoo
"""

import json
from mcp.server.fastmcp import FastMCP

def register_sales_resources(mcp: FastMCP) -> None:
    """Registra recursos relacionados con ventas"""
    
    @mcp.resource(
        "odoo://sales/orders",
        description="Lista órdenes de venta con filtros opcionales"
    )
    def list_sales_orders(
        limit: int = 10,
        offset: int = 0,
        state: str = None,
        date_from: str = None,
        date_to: str = None
    ) -> str:
        """
        Lista órdenes de venta con filtros opcionales
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            state: Estado de las órdenes (e.g., 'draft', 'sale', 'done')
            date_from: Fecha inicial en formato YYYY-MM-DD
            date_to: Fecha final en formato YYYY-MM-DD
            
        Returns:
            JSON con las órdenes de venta
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = []
            
            if state:
                domain.append(("state", "=", state))
                
            if date_from:
                domain.append(("date_order", ">=", date_from))
                
            if date_to:
                domain.append(("date_order", "<=", date_to))
            
            # Campos a recuperar
            fields = [
                "name", "partner_id", "date_order", "amount_total", 
                "state", "invoice_status", "user_id"
            ]
            
            # Ejecutar búsqueda
            orders = odoo_client.search_read(
                "sale.order", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset,
                order="date_order desc"
            )
            
            return json.dumps(orders, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://sales/order/{order_id}",
        description="Obtiene detalles de una orden de venta específica"
    )
    def get_sales_order(order_id: str) -> str:
        """
        Obtiene detalles de una orden de venta específica
        
        Args:
            order_id: ID de la orden de venta
            
        Returns:
            JSON con los detalles de la orden
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Convertir order_id a entero
            try:
                order_id_int = int(order_id)
            except ValueError:
                return json.dumps({"error": f"ID de orden inválido: {order_id}"}, indent=2)
            
            # Obtener la orden
            order = odoo_client.read_records("sale.order", [order_id_int])
            
            if not order:
                return json.dumps({"error": f"Orden no encontrada: {order_id}"}, indent=2)
            
            order_data = order[0]
            
            # Obtener líneas de la orden
            if "order_line" in order_data:
                line_ids = order_data["order_line"]
                lines = odoo_client.read_records(
                    "sale.order.line", 
                    line_ids,
                    fields=["product_id", "name", "product_uom_qty", "price_unit", "price_subtotal"]
                )
                order_data["order_lines"] = lines
            
            return json.dumps(order_data, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://sales/products",
        description="Lista productos vendibles"
    )
    def list_sale_products(
        limit: int = 20,
        offset: int = 0,
        category_id: str = None
    ) -> str:
        """
        Lista productos vendibles
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            category_id: ID de categoría para filtrar productos
            
        Returns:
            JSON con los productos vendibles
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = [("sale_ok", "=", True)]
            
            if category_id:
                try:
                    category_id_int = int(category_id)
                    domain.append(("categ_id", "=", category_id_int))
                except ValueError:
                    return json.dumps({"error": f"ID de categoría inválido: {category_id}"}, indent=2)
            
            # Campos a recuperar
            fields = [
                "name", "default_code", "list_price", "standard_price",
                "categ_id", "type", "uom_id", "description_sale"
            ]
            
            # Ejecutar búsqueda
            products = odoo_client.search_read(
                "product.product", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset
            )
            
            return json.dumps(products, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://sales/customers",
        description="Lista clientes para ventas"
    )
    def list_customers(
        limit: int = 20,
        offset: int = 0,
        customer: bool = True
    ) -> str:
        """
        Lista clientes para ventas
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            customer: Si es True, filtra solo contactos marcados como clientes
            
        Returns:
            JSON con los clientes
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = []
            
            if customer:
                # El campo puede variar según la versión de Odoo
                # En Odoo 13+, se usa customer_rank > 0
                # En versiones anteriores, se usa customer = True
                try:
                    # Verificar si existe el campo customer_rank
                    fields_info = odoo_client.get_model_fields("res.partner")
                    if "customer_rank" in fields_info:
                        domain.append(("customer_rank", ">", 0))
                    else:
                        domain.append(("customer", "=", True))
                except Exception:
                    # Si falla, intentar con customer = True
                    domain.append(("customer", "=", True))
            
            # Campos a recuperar
            fields = [
                "name", "email", "phone", "mobile", "street", "city",
                "country_id", "vat", "category_id"
            ]
            
            # Ejecutar búsqueda
            customers = odoo_client.search_read(
                "res.partner", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset
            )
            
            return json.dumps(customers, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

def register_purchase_resources(mcp: FastMCP) -> None:
    """Registra recursos relacionados con compras"""
    
    @mcp.resource(
        "odoo://purchase/orders",
        description="Lista órdenes de compra con filtros opcionales"
    )
    def list_purchase_orders(
        limit: int = 10,
        offset: int = 0,
        state: str = None,
        date_from: str = None,
        date_to: str = None
    ) -> str:
        """
        Lista órdenes de compra con filtros opcionales
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            state: Estado de las órdenes (e.g., 'draft', 'purchase', 'done')
            date_from: Fecha inicial en formato YYYY-MM-DD
            date_to: Fecha final en formato YYYY-MM-DD
            
        Returns:
            JSON con las órdenes de compra
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = []
            
            if state:
                domain.append(("state", "=", state))
                
            if date_from:
                domain.append(("date_order", ">=", date_from))
                
            if date_to:
                domain.append(("date_order", "<=", date_to))
            
            # Campos a recuperar
            fields = [
                "name", "partner_id", "date_order", "amount_total", 
                "state", "invoice_status", "user_id", "date_planned"
            ]
            
            # Ejecutar búsqueda
            orders = odoo_client.search_read(
                "purchase.order", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset,
                order="date_order desc"
            )
            
            return json.dumps(orders, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://purchase/order/{order_id}",
        description="Obtiene detalles de una orden de compra específica"
    )
    def get_purchase_order(order_id: str) -> str:
        """
        Obtiene detalles de una orden de compra específica
        
        Args:
            order_id: ID de la orden de compra
            
        Returns:
            JSON con los detalles de la orden
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Convertir order_id a entero
            try:
                order_id_int = int(order_id)
            except ValueError:
                return json.dumps({"error": f"ID de orden inválido: {order_id}"}, indent=2)
            
            # Obtener la orden
            order = odoo_client.read_records("purchase.order", [order_id_int])
            
            if not order:
                return json.dumps({"error": f"Orden no encontrada: {order_id}"}, indent=2)
            
            order_data = order[0]
            
            # Obtener líneas de la orden
            if "order_line" in order_data:
                line_ids = order_data["order_line"]
                lines = odoo_client.read_records(
                    "purchase.order.line", 
                    line_ids,
                    fields=["product_id", "name", "product_qty", "price_unit", "price_subtotal", "date_planned"]
                )
                order_data["order_lines"] = lines
            
            return json.dumps(order_data, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://purchase/suppliers",
        description="Lista proveedores"
    )
    def list_suppliers(
        limit: int = 20,
        offset: int = 0
    ) -> str:
        """
        Lista proveedores
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            
        Returns:
            JSON con los proveedores
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            # El campo puede variar según la versión de Odoo
            # En Odoo 13+, se usa supplier_rank > 0
            # En versiones anteriores, se usa supplier = True
            domain = []
            
            try:
                # Verificar si existe el campo supplier_rank
                fields_info = odoo_client.get_model_fields("res.partner")
                if "supplier_rank" in fields_info:
                    domain.append(("supplier_rank", ">", 0))
                else:
                    domain.append(("supplier", "=", True))
            except Exception:
                # Si falla, intentar con supplier = True
                domain.append(("supplier", "=", True))
            
            # Campos a recuperar
            fields = [
                "name", "email", "phone", "mobile", "street", "city",
                "country_id", "vat", "category_id"
            ]
            
            # Ejecutar búsqueda
            suppliers = odoo_client.search_read(
                "res.partner", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset
            )
            
            return json.dumps(suppliers, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

def register_inventory_resources(mcp: FastMCP) -> None:
    """Registra recursos relacionados con inventario"""
    
    @mcp.resource(
        "odoo://inventory/products",
        description="Lista productos en inventario"
    )
    def list_inventory_products(
        limit: int = 20,
        offset: int = 0,
        category_id: str = None,
        location_id: str = None
    ) -> str:
        """
        Lista productos en inventario
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            category_id: ID de categoría para filtrar productos
            location_id: ID de ubicación para filtrar stock
            
        Returns:
            JSON con los productos y su stock
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = [("type", "=", "product")]  # Solo productos almacenables
            
            if category_id:
                try:
                    category_id_int = int(category_id)
                    domain.append(("categ_id", "=", category_id_int))
                except ValueError:
                    return json.dumps({"error": f"ID de categoría inválido: {category_id}"}, indent=2)
            
            # Construir contexto para la ubicación
            context = {}
            if location_id:
                try:
                    location_id_int = int(location_id)
                    context["location"] = location_id_int
                except ValueError:
                    return json.dumps({"error": f"ID de ubicación inválido: {location_id}"}, indent=2)
            
            # Campos a recuperar
            fields = [
                "name", "default_code", "categ_id", "qty_available",
                "virtual_available", "incoming_qty", "outgoing_qty"
            ]
            
            # Ejecutar búsqueda
            products = odoo_client.execute_method(
                "product.product", 
                "search_read", 
                domain,
                {
                    "fields": fields,
                    "limit": limit,
                    "offset": offset,
                    "context": context
                }
            )
            
            return json.dumps(products, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://inventory/stock/{location_id}",
        description="Obtiene niveles de stock en una ubicación específica"
    )
    def get_location_stock(location_id: str) -> str:
        """
        Obtiene niveles de stock en una ubicación específica
        
        Args:
            location_id: ID de la ubicación
            
        Returns:
            JSON con los niveles de stock
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Convertir location_id a entero
            try:
                location_id_int = int(location_id)
            except ValueError:
                return json.dumps({"error": f"ID de ubicación inválido: {location_id}"}, indent=2)
            
            # Verificar que la ubicación existe
            location = odoo_client.read_records("stock.location", [location_id_int], ["name", "complete_name"])
            
            if not location:
                return json.dumps({"error": f"Ubicación no encontrada: {location_id}"}, indent=2)
            
            location_data = location[0]
            
            # Obtener quants (cantidades de stock) en la ubicación
            quants = odoo_client.search_read(
                "stock.quant",
                [("location_id", "=", location_id_int)],
                fields=["product_id", "quantity", "reserved_quantity"]
            )
            
            # Enriquecer con información de producto
            for quant in quants:
                if quant.get("product_id"):
                    product_id = quant["product_id"][0]
                    product_info = odoo_client.read_records(
                        "product.product",
                        [product_id],
                        ["name", "default_code", "categ_id"]
                    )
                    if product_info:
                        quant["product_details"] = product_info[0]
            
            result = {
                "location": location_data,
                "stock_items": quants
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://inventory/movements",
        description="Lista movimientos de inventario"
    )
    def list_inventory_movements(
        limit: int = 20,
        offset: int = 0,
        date_from: str = None,
        date_to: str = None,
        product_id: str = None
    ) -> str:
        """
        Lista movimientos de inventario
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            date_from: Fecha inicial en formato YYYY-MM-DD
            date_to: Fecha final en formato YYYY-MM-DD
            product_id: ID de producto para filtrar movimientos
            
        Returns:
            JSON con los movimientos de inventario
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = []
            
            if date_from:
                domain.append(("date", ">=", date_from))
                
            if date_to:
                domain.append(("date", "<=", date_to))
                
            if product_id:
                try:
                    product_id_int = int(product_id)
                    domain.append(("product_id", "=", product_id_int))
                except ValueError:
                    return json.dumps({"error": f"ID de producto inválido: {product_id}"}, indent=2)
            
            # Campos a recuperar
            fields = [
                "name", "product_id", "product_uom_qty", "date",
                "location_id", "location_dest_id", "state", "origin"
            ]
            
            # Ejecutar búsqueda
            moves = odoo_client.search_read(
                "stock.move", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset,
                order="date desc"
            )
            
            return json.dumps(moves, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

def register_accounting_resources(mcp: FastMCP) -> None:
    """Registra recursos relacionados con contabilidad"""
    
    @mcp.resource(
        "odoo://accounting/accounts",
        description="Lista cuentas contables"
    )
    def list_accounts(
        limit: int = 50,
        offset: int = 0,
        account_type: str = None
    ) -> str:
        """
        Lista cuentas contables
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            account_type: Tipo de cuenta para filtrar (e.g., 'receivable', 'payable', 'liquidity')
            
        Returns:
            JSON con las cuentas contables
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = []
            
            if account_type:
                domain.append(("user_type_id.type", "=", account_type))
            
            # Campos a recuperar
            fields = [
                "code", "name", "user_type_id", "company_id",
                "currency_id", "reconcile", "deprecated"
            ]
            
            # Ejecutar búsqueda
            accounts = odoo_client.search_read(
                "account.account", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset,
                order="code"
            )
            
            return json.dumps(accounts, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://accounting/journal_entries",
        description="Lista asientos contables"
    )
    def list_journal_entries(
        limit: int = 20,
        offset: int = 0,
        date_from: str = None,
        date_to: str = None,
        journal_id: str = None,
        state: str = "posted"
    ) -> str:
        """
        Lista asientos contables
        
        Args:
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir (para paginación)
            date_from: Fecha inicial en formato YYYY-MM-DD
            date_to: Fecha final en formato YYYY-MM-DD
            journal_id: ID del diario contable para filtrar
            state: Estado de los asientos ('draft', 'posted', 'cancel')
            
        Returns:
            JSON con los asientos contables
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Construir dominio
            domain = []
            
            if state:
                domain.append(("state", "=", state))
                
            if date_from:
                domain.append(("date", ">=", date_from))
                
            if date_to:
                domain.append(("date", "<=", date_to))
                
            if journal_id:
                try:
                    journal_id_int = int(journal_id)
                    domain.append(("journal_id", "=", journal_id_int))
                except ValueError:
                    return json.dumps({"error": f"ID de diario inválido: {journal_id}"}, indent=2)
            
            # Campos a recuperar
            fields = [
                "name", "ref", "date", "journal_id", "state", 
                "amount_total", "amount_total_signed"
            ]
            
            # Ejecutar búsqueda
            entries = odoo_client.search_read(
                "account.move", 
                domain, 
                fields=fields, 
                limit=limit,
                offset=offset,
                order="date desc, id desc"
            )
            
            return json.dumps(entries, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)
    
    @mcp.resource(
        "odoo://accounting/reports/{report_type}",
        description="Obtiene informes financieros"
    )
    def get_financial_report(
        report_type: str,
        date_from: str = None,
        date_to: str = None
    ) -> str:
        """
        Obtiene informes financieros
        
        Args:
            report_type: Tipo de informe ('balance_sheet', 'profit_loss', 'aged_receivable', 'aged_payable')
            date_from: Fecha inicial en formato YYYY-MM-DD
            date_to: Fecha final en formato YYYY-MM-DD
            
        Returns:
            JSON con el informe financiero
        """
        from .odoo_client import get_odoo_client
        
        try:
            odoo_client = get_odoo_client()
            
            # Validar tipo de informe
            valid_report_types = ["balance_sheet", "profit_loss", "aged_receivable", "aged_payable"]
            if report_type not in valid_report_types:
                return json.dumps({
                    "error": f"Tipo de informe inválido: {report_type}. Valores válidos: {', '.join(valid_report_types)}"
                }, indent=2)
            
            # Construir resultado según el tipo de informe
            result = {
                "report_type": report_type,
                "date_range": {
                    "from": date_from,
                    "to": date_to
                }
            }
            
            if report_type == "balance_sheet":
                # Obtener activos
                assets_domain = [
                    ("account_id.user_type_id.internal_group", "=", "asset")
                ]
                
                if date_to:
                    assets_domain.append(("date", "<=", date_to))
                    
                assets_data = odoo_client.search_read(
                    "account.move.line",
                    assets_domain,
                    fields=["account_id", "balance"],
                    limit=1000
                )
                
                # Obtener pasivos
                liabilities_domain = [
                    ("account_id.user_type_id.internal_group", "=", "liability")
                ]
                
                if date_to:
                    liabilities_domain.append(("date", "<=", date_to))
                    
                liabilities_data = odoo_client.search_read(
                    "account.move.line",
                    liabilities_domain,
                    fields=["account_id", "balance"],
                    limit=1000
                )
                
                # Obtener patrimonio
                equity_domain = [
                    ("account_id.user_type_id.internal_group", "=", "equity")
                ]
                
                if date_to:
                    equity_domain.append(("date", "<=", date_to))
                    
                equity_data = odoo_client.search_read(
                    "account.move.line",
                    equity_domain,
                    fields=["account_id", "balance"],
                    limit=1000
                )
                
                # Calcular totales
                total_assets = sum(line["balance"] for line in assets_data)
                total_liabilities = sum(line["balance"] for line in liabilities_data)
                total_equity = sum(line["balance"] for line in equity_data)
                
                result["balance_sheet"] = {
                    "assets": {
                        "total": total_assets,
                        "accounts": {}
                    },
                    "liabilities": {
                        "total": total_liabilities,
                        "accounts": {}
                    },
                    "equity": {
                        "total": total_equity,
                        "accounts": {}
                    }
                }
                
                # Agrupar por cuenta
                for line in assets_data:
                    account_id = line["account_id"][0]
                    account_name = line["account_id"][1]
                    if account_id not in result["balance_sheet"]["assets"]["accounts"]:
                        result["balance_sheet"]["assets"]["accounts"][account_id] = {
                            "name": account_name,
                            "balance": 0
                        }
                    result["balance_sheet"]["assets"]["accounts"][account_id]["balance"] += line["balance"]
                
                for line in liabilities_data:
                    account_id = line["account_id"][0]
                    account_name = line["account_id"][1]
                    if account_id not in result["balance_sheet"]["liabilities"]["accounts"]:
                        result["balance_sheet"]["liabilities"]["accounts"][account_id] = {
                            "name": account_name,
                            "balance": 0
                        }
                    result["balance_sheet"]["liabilities"]["accounts"][account_id]["balance"] += line["balance"]
                
                for line in equity_data:
                    account_id = line["account_id"][0]
                    account_name = line["account_id"][1]
                    if account_id not in result["balance_sheet"]["equity"]["accounts"]:
                        result["balance_sheet"]["equity"]["accounts"][account_id] = {
                            "name": account_name,
                            "balance": 0
                        }
                    result["balance_sheet"]["equity"]["accounts"][account_id]["balance"] += line["balance"]
                
            elif report_type == "profit_loss":
                # Obtener ingresos
                income_domain = [
                    ("account_id.user_type_id.internal_group", "=", "income")
                ]
                
                if date_from:
                    income_domain.append(("date", ">=", date_from))
                    
                if date_to:
                    income_domain.append(("date", "<=", date_to))
                    
                income_data = odoo_client.search_read(
                    "account.move.line",
                    income_domain,
                    fields=["account_id", "balance"],
                    limit=1000
                )
                
                # Obtener gastos
                expense_domain = [
                    ("account_id.user_type_id.internal_group", "=", "expense")
                ]
                
                if date_from:
                    expense_domain.append(("date", ">=", date_from))
                    
                if date_to:
                    expense_domain.append(("date", "<=", date_to))
                    
                expense_data = odoo_client.search_read(
                    "account.move.line",
                    expense_domain,
                    fields=["account_id", "balance"],
                    limit=1000
                )
                
                # Calcular totales
                total_income = sum(line["balance"] for line in income_data)
                total_expenses = sum(line["balance"] for line in expense_data)
                net_profit = total_income - total_expenses
                
                result["profit_loss"] = {
                    "income": {
                        "total": total_income,
                        "accounts": {}
                    },
                    "expenses": {
                        "total": total_expenses,
                        "accounts": {}
                    },
                    "net_profit": net_profit
                }
                
                # Agrupar por cuenta
                for line in income_data:
                    account_id = line["account_id"][0]
                    account_name = line["account_id"][1]
                    if account_id not in result["profit_loss"]["income"]["accounts"]:
                        result["profit_loss"]["income"]["accounts"][account_id] = {
                            "name": account_name,
                            "balance": 0
                        }
                    result["profit_loss"]["income"]["accounts"][account_id]["balance"] += line["balance"]
                
                for line in expense_data:
                    account_id = line["account_id"][0]
                    account_name = line["account_id"][1]
                    if account_id not in result["profit_loss"]["expenses"]["accounts"]:
                        result["profit_loss"]["expenses"]["accounts"][account_id] = {
                            "name": account_name,
                            "balance": 0
                        }
                    result["profit_loss"]["expenses"]["accounts"][account_id]["balance"] += line["balance"]
                
            elif report_type in ["aged_receivable", "aged_payable"]:
                # Determinar tipo de cuenta
                account_type = "receivable" if report_type == "aged_receivable" else "payable"
                
                # Obtener cuentas por cobrar/pagar
                domain = [
                    ("account_id.user_type_id.type", "=", account_type),
                    ("full_reconcile_id", "=", False),  # No conciliado completamente
                    ("balance", "!=", 0)  # Con saldo pendiente
                ]
                
                if date_to:
                    domain.append(("date", "<=", date_to))
                
                move_lines = odoo_client.search_read(
                    "account.move.line",
                    domain,
                    fields=[
                        "partner_id", "account_id", "date", "date_maturity",
                        "balance", "amount_currency", "currency_id"
                    ],
                    limit=1000
                )
                
                # Agrupar por socio y calcular antigüedad
                partners = {}
                
                for line in move_lines:
                    partner_id = line["partner_id"][0] if line["partner_id"] else 0
                    partner_name = line["partner_id"][1] if line["partner_id"] else "Sin socio"
                    
                    if partner_id not in partners:
                        partners[partner_id] = {
                            "name": partner_name,
                            "total": 0,
                            "buckets": {
                                "not_due": 0,
                                "1_30": 0,
                                "31_60": 0,
                                "61_90": 0,
                                "91_plus": 0
                            },
                            "lines": []
                        }
                    
                    # Calcular antigüedad
                    date_maturity = line.get("date_maturity") or line["date"]
                    if isinstance(date_maturity, str):
                        date_maturity = date_maturity.split(" ")[0]  # Obtener solo la fecha
                    
                    days_due = 0
                    if date_to and date_maturity:
                        from datetime import datetime
                        maturity_date = datetime.strptime(date_maturity, "%Y-%m-%d")
                        end_date = datetime.strptime(date_to, "%Y-%m-%d")
                        days_due = (end_date - maturity_date).days
                    
                    # Asignar a bucket
                    bucket = "not_due"
                    if days_due > 0:
                        if days_due <= 30:
                            bucket = "1_30"
                        elif days_due <= 60:
                            bucket = "31_60"
                        elif days_due <= 90:
                            bucket = "61_90"
                        else:
                            bucket = "91_plus"
                    
                    # Actualizar totales
                    balance = abs(line["balance"])  # Usar valor absoluto
                    partners[partner_id]["total"] += balance
                    partners[partner_id]["buckets"][bucket] += balance
                    
                    # Añadir línea
                    partners[partner_id]["lines"].append({
                        "date": line["date"],
                        "date_maturity": date_maturity,
                        "days_due": days_due,
                        "balance": line["balance"],
                        "account": line["account_id"][1]
                    })
                
                # Ordenar por total
                sorted_partners = sorted(
                    partners.items(),
                    key=lambda x: x[1]["total"],
                    reverse=True
                )
                
                # Calcular totales generales
                total_amount = sum(partner["total"] for _, partner in partners.items())
                total_buckets = {
                    "not_due": 0,
                    "1_30": 0,
                    "31_60": 0,
                    "61_90": 0,
                    "91_plus": 0
                }
                
                for _, partner in partners.items():
                    for bucket, amount in partner["buckets"].items():
                        total_buckets[bucket] += amount
                
                result[report_type] = {
                    "total_amount": total_amount,
                    "buckets": total_buckets,
                    "partners": [
                        {"id": k, **v} for k, v in sorted_partners
                    ]
                }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

def register_all_resources(mcp: FastMCP) -> None:
    """Registra todos los recursos disponibles"""
    register_sales_resources(mcp)
    register_purchase_resources(mcp)
    register_inventory_resources(mcp)
    register_accounting_resources(mcp)
