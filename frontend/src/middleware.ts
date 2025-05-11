import { NextRequest, NextResponse } from 'next/server'

export default function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname
  const role = req.cookies.get('role')?.value

  switch (role) {
    case "user": {
      if (!path.startsWith("/admin") && path !== "/login")
        return NextResponse.next()
      return NextResponse.redirect(new URL("/", req.nextUrl))  
    }
    case "manager": {
      if (path.startsWith("/admin") && !path.startsWith("/admin/users"))
        return NextResponse.next()
      return NextResponse.redirect(new URL("/admin", req.nextUrl))  
    }
    case "admin": {
      if (path.startsWith("/admin"))
        return NextResponse.next()
      return NextResponse.redirect(new URL("/admin", req.nextUrl))  
    }
    default: {
      if (!path.startsWith("/admin"))
        return NextResponse.next()
      return NextResponse.redirect(new URL("/", req.nextUrl))  
    }
  }
}
 
// Routes Middleware should not run on
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)'],
}