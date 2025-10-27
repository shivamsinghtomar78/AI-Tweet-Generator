import * as React from "react"
import { cn } from "../../lib/utils"

const Slider = React.forwardRef(({ className, ...props }, ref) => (
  <input
    type="range"
    className={cn(
      "w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer slider transition-all duration-200 hover:h-3",
      className
    )}
    ref={ref}
    {...props}
  />
))
Slider.displayName = "Slider"

export { Slider }