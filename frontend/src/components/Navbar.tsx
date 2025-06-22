
export const Navbar = () => {
  return (
    <header className="fixed top-0 left-0 w-full z-50 bg-sky-100/50 backdrop-blur-sm">
      <nav className="flex items-center justify-start p-6 lg:px-8">
        <a href="/" className="no-underline">
          <h1 className="text-2xl font-bold">
            <span className="text-slate-800">Git</span>
            <span className="text-orange-500">Cast</span>
          </h1>
        </a>
      </nav>
    </header>
  );
}; 
