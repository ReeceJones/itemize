import { Card, Stack, Text, Title, UnstyledButton } from "@mantine/core"
import Link from "next/link"
import { Itemize } from "@/util/api"

export default function ItemizeCard({ itemize }: { itemize: Itemize }) {
  return (
    <UnstyledButton component={Link} key={itemize.slug} href={`/${itemize.owner}/${itemize.slug}`}>
      <Card shadow="sm" padding={0} radius="md" withBorder>
        <Stack m={10}>
          <Text size="xl" fw={500}>{itemize.name}</Text>
          <Text>{itemize.description}</Text>
        </Stack>
      </Card>
    </UnstyledButton>
  )
}