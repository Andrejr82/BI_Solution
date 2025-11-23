/**
 * ReportEditor Component
 * Editor de texto rico usando TipTap
 */

'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Button } from '@/components/ui/button';
import { Toggle } from '@/components/ui/toggle';
import { 
  Bold, 
  Italic, 
  List, 
  ListOrdered, 
  Heading1, 
  Heading2, 
  Quote, 
  Undo, 
  Redo 
} from 'lucide-react';

interface ReportEditorProps {
  content: any;
  onChange: (content: any) => void;
  editable?: boolean;
}

export function ReportEditor({ content, onChange, editable = true }: ReportEditorProps) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: content || '<p>Comece a escrever seu relatório...</p>',
    editable,
    onUpdate: ({ editor }) => {
      onChange(editor.getJSON());
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none min-h-[300px] p-4 border rounded-md',
      },
    },
  });

  if (!editor) {
    return null;
  }

  return (
    <div className="space-y-2">
      {editable && (
        <div className="flex flex-wrap gap-2 p-2 border rounded-md bg-muted/20">
          <Toggle
            size="sm"
            pressed={editor.isActive('bold')}
            onPressedChange={() => editor.chain().focus().toggleBold().run()}
          >
            <Bold className="h-4 w-4" />
          </Toggle>
          
          <Toggle
            size="sm"
            pressed={editor.isActive('italic')}
            onPressedChange={() => editor.chain().focus().toggleItalic().run()}
          >
            <Italic className="h-4 w-4" />
          </Toggle>

          <div className="w-px h-6 bg-border mx-1" />

          <Toggle
            size="sm"
            pressed={editor.isActive('heading', { level: 1 })}
            onPressedChange={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          >
            <Heading1 className="h-4 w-4" />
          </Toggle>

          <Toggle
            size="sm"
            pressed={editor.isActive('heading', { level: 2 })}
            onPressedChange={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          >
            <Heading2 className="h-4 w-4" />
          </Toggle>

          <div className="w-px h-6 bg-border mx-1" />

          <Toggle
            size="sm"
            pressed={editor.isActive('bulletList')}
            onPressedChange={() => editor.chain().focus().toggleBulletList().run()}
          >
            <List className="h-4 w-4" />
          </Toggle>

          <Toggle
            size="sm"
            pressed={editor.isActive('orderedList')}
            onPressedChange={() => editor.chain().focus().toggleOrderedList().run()}
          >
            <ListOrdered className="h-4 w-4" />
          </Toggle>

          <Toggle
            size="sm"
            pressed={editor.isActive('blockquote')}
            onPressedChange={() => editor.chain().focus().toggleBlockquote().run()}
          >
            <Quote className="h-4 w-4" />
          </Toggle>

          <div className="flex-1" />

          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().undo()}
          >
            <Undo className="h-4 w-4" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().redo()}
          >
            <Redo className="h-4 w-4" />
          </Button>
        </div>
      )}

      <EditorContent editor={editor} />
    </div>
  );
}
