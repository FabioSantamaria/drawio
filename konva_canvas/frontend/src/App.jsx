import React, { useEffect, useRef, useState } from 'react'
import { withStreamlitConnection, Streamlit } from 'streamlit-component-lib'
import { Stage, Layer, Line } from 'react-konva'

function App({ args }) {
  const width = args?.width ?? 900
  const height = args?.height ?? 520
  const color = args?.color ?? '#000000'
  const strokeWidth = args?.strokeWidth ?? 4
  const clear = args?.clear ?? false

  const [lines, setLines] = useState([])
  const isDrawing = useRef(false)
  const stageRef = useRef(null)

  useEffect(() => {
    Streamlit.setComponentReady()
    Streamlit.setFrameHeight(height + 60)
  }, [height])

  useEffect(() => {
    if (clear) {
      setLines([])
      Streamlit.setComponentValue({ dataUrl: null, linesCount: 0 })
    }
  }, [clear])

  const handleMouseDown = (e) => {
    isDrawing.current = true
    const pos = e.target.getStage().getPointerPosition()
    setLines((prev) => prev.concat([{ points: [pos.x, pos.y], color, strokeWidth }]))
  }

  const handleMouseMove = (e) => {
    if (!isDrawing.current) return
    const stage = e.target.getStage()
    const point = stage.getPointerPosition()
    setLines((prev) => {
      const lastLine = prev[prev.length - 1]
      const newLast = { ...lastLine, points: lastLine.points.concat([point.x, point.y]) }
      return prev.slice(0, -1).concat(newLast)
    })
  }

  const handleMouseUp = () => {
    isDrawing.current = false
  }

  const handleMouseLeave = () => {
    isDrawing.current = false
  }

  const exportImage = () => {
    const stage = stageRef.current
    if (!stage) return
    const dataUrl = stage.toDataURL({ pixelRatio: 1 })
    Streamlit.setComponentValue({ dataUrl, linesCount: lines.length })
  }

  return (
    <div style={{ userSelect: 'none' }}>
      <Stage
        ref={stageRef}
        width={width}
        height={height}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        onTouchStart={handleMouseDown}
        onTouchMove={handleMouseMove}
        onTouchEnd={handleMouseUp}
      >
        <Layer>
          {lines.map((line, i) => (
            <Line
              key={i}
              points={line.points}
              stroke={line.color}
              strokeWidth={line.strokeWidth}
              tension={0}
              lineCap="round"
              lineJoin="round"
            />
          ))}
        </Layer>
      </Stage>
      <div style={{ marginTop: 8 }}>
        <button onClick={exportImage}>Export</button>
      </div>
    </div>
  )
}

export default withStreamlitConnection(App)