export function WidgetContent({ widget, onClose, onUpdate }) {
  switch (widget.widget_type) {
    case "financeiro":
      return <FinanceWidget widget={widget} onUpdate={onUpdate} />;
    case "ordens":
      return <OrdersWidget widget={widget} onUpdate={onUpdate} />;
    case "posts_instagram":
      return <PostsWidget widget={widget} onUpdate={onUpdate} />;
    case "docs":
      return <DocsWidget widget={widget} />;
    default:
      return (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 gap-2">
          <div className="w-12 h-12 border border-dashed border-gray-600 rounded flex items-center justify-center">
            <span className="text-xl">?</span>
          </div>
          <p className="text-sm">Widget desconhecido: {widget.widget_type}</p>
        </div>
      );
  }
}
