import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Strategy Lab | Gemini 3",
    description: "Advanced Forex Strategy Research & Backtesting",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" className="dark" suppressHydrationWarning>
            <body className="bg-background text-foreground min-h-screen antialiased" suppressHydrationWarning>
                <div className="flex min-h-screen flex-col">
                    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-background/80 backdrop-blur-xl">
                        <div className="container mx-auto flex h-14 items-center px-4">
                            <div className="flex items-center gap-2 font-bold text-xl tracking-tighter">
                                <span className="text-primary">ANTIGRAVITY</span>
                                <span className="text-muted-foreground">LABS</span>
                            </div>
                        </div>
                    </header>
                    <main className="flex-1 container mx-auto p-4 md:p-8">
                        {children}
                    </main>
                </div>
            </body>
        </html>
    );
}
